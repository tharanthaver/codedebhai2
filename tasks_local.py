import os
import uuid
import time
import logging
from celery import current_task
from celery_config_local import celery_app
from db_helper import DatabaseHelper
import concurrent.futures
from datetime import datetime

# Import functions from app.py
from app import (
    extract_text_from_pdf, split_questions, solve_coding_problem,
    execute_code, create_screenshot, generate_word_doc, process_question
)

# Initialize database helper
db_helper = DatabaseHelper()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks_local.test_simple_task')
def test_simple_task(self, message="Hello from Celery!"):
    """
    Simple test task to verify Celery is working
    """
    task_id = self.request.id
    logger.info(f"Starting simple test task {task_id}")
    
    # Simulate some work
    for i in range(5):
        current_task.update_state(
            state='PROGRESS',
            meta={'progress': i * 20, 'status': f'Step {i+1}/5'}
        )
        time.sleep(1)
    
    logger.info(f"Test task {task_id} completed")
    return {'status': 'SUCCESS', 'message': message, 'task_id': task_id}

@celery_app.task(bind=True, name='tasks_local.process_pdf_async')
def process_pdf_async(self, pdf_path, name, reg_number, language, phone_number, 
                     file_filename, confirmed=False):
    """
    Asynchronous PDF processing task - LOCAL VERSION
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(f"Starting PDF processing task {task_id} for user {phone_number}")
    
    try:
        # Update task status
        current_task.update_state(
            state='PROCESSING',
            meta={
                'status': 'Extracting text from PDF...',
                'progress': 10,
                'stage': 'pdf_extraction'
            }
        )
        
        # Extract text from PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        questions = split_questions(pdf_text)
        
        # Calculate credits required
        base_credits = 1
        extra_questions = max(0, len(questions) - 20)
        total_credits_required = base_credits + extra_questions
        
        # Check credits
        current_user = db_helper.get_user_by_phone(phone_number)
        if not current_user or current_user['credits'] < total_credits_required:
            raise Exception(f"Insufficient credits. Need {total_credits_required}, have {current_user['credits'] if current_user else 0}")
        
        # If not confirmed and exceeds 20 questions, require confirmation
        if not confirmed and len(questions) > 20:
            return {
                'status': 'CONFIRMATION_REQUIRED',
                'requires_confirmation': True,
                'question_count': len(questions),
                'total_credits_required': total_credits_required,
                'extra_questions': extra_questions,
                'message': f"This PDF contains {len(questions)} questions. Processing will cost {total_credits_required} credits. Do you want to continue?"
            }
        
        current_task.update_state(
            state='PROCESSING',
            meta={
                'status': f'Processing {len(questions)} questions...',
                'progress': 25,
                'stage': 'question_processing',
                'question_count': len(questions)
            }
        )
        
        # Process questions in parallel
        solutions_display = []
        screenshots = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:  # Reduced for local testing
            futures = [executor.submit(process_question, q, language) for q in questions]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                sol, scr = future.result()
                solutions_display.append(sol)
                screenshots.append(scr)
                
                # Update progress
                progress = 25 + (i + 1) * 50 // len(questions)
                current_task.update_state(
                    state='PROCESSING',
                    meta={
                        'status': f'Processed {i + 1}/{len(questions)} questions',
                        'progress': progress,
                        'stage': 'question_processing'
                    }
                )
        
        current_task.update_state(
            state='PROCESSING',
            meta={
                'status': 'Generating Word document...',
                'progress': 85,
                'stage': 'document_generation'
            }
        )
        
        # Generate Word document
        output_file = os.path.join('temp', f"solutions_{uuid.uuid4().hex}.docx")
        generated_path = generate_word_doc(name, reg_number, questions, solutions_display, screenshots, output_file)
        
        if not os.path.exists(generated_path):
            raise Exception("Document generation failed")
        
        # Calculate metrics
        successful_solutions = [sol for sol in solutions_display if sol and not sol.startswith("Error")]
        questions_solved = len(successful_solutions)
        questions_failed = len(questions) - questions_solved
        failed_questions = [q for q, sol in zip(questions, solutions_display) if not sol or sol.startswith("Error")]
        is_fully_solved = questions_solved == len(questions)
        
        # Record submission
        submission_record = db_helper.insert_submission(
            phone_number=phone_number,
            pdf_name=file_filename,
            questions_count=len(questions),
            questions_solved=questions_solved,
            questions_failed=questions_failed,
            failed_questions=failed_questions,
            solved=is_fully_solved,
            error_details=None if is_fully_solved else f"{questions_failed} questions failed to solve",
            processing_time_seconds=(time.time() - start_time),
            submission_type='pdf_async_local'
        )
        
        # Deduct credits
        updated_user = db_helper.deduct_credits_by_count(phone_number, len(questions))
        
        logger.info(f"PDF processing task {task_id} completed successfully")
        
        return {
            'status': 'SUCCESS',
            'file_path': generated_path,
            'questions_count': len(questions),
            'questions_solved': questions_solved,
            'questions_failed': questions_failed,
            'processing_time': time.time() - start_time,
            'submission_id': submission_record.get('id') if submission_record else None,
            'credits_used': total_credits_required,
            'new_credit_balance': updated_user.get('credits', 0) if updated_user else 0
        }
        
    except Exception as e:
        logger.error(f"PDF processing task {task_id} failed: {str(e)}")
        
        # Update task state to failure
        current_task.update_state(
            state='FAILURE',
            meta={
                'status': 'Processing failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        raise Exception(f"PDF processing failed: {str(e)}")

@celery_app.task(bind=True, name='tasks_local.process_single_question')
def process_single_question(self, question, language='python'):
    """
    Fast processing for single questions - LOCAL VERSION
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(f"Processing single question task {task_id}")
    
    try:
        current_task.update_state(
            state='PROCESSING',
            meta={
                'status': 'Solving question...',
                'progress': 50,
                'stage': 'solving'
            }
        )
        
        solution, screenshot = process_question(question, language)
        
        return {
            'status': 'SUCCESS',
            'solution': solution,
            'screenshot': screenshot,
            'processing_time': time.time() - start_time
        }
        
    except Exception as e:
        logger.error(f"Single question processing task {task_id} failed: {str(e)}")
        
        current_task.update_state(
            state='FAILURE',
            meta={
                'status': 'Processing failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        raise Exception(f"Single question processing failed: {str(e)}")

if __name__ == '__main__':
    print("Tasks registered successfully!")
    print("Available tasks:")
    print("- test_simple_task")
    print("- process_pdf_async")
    print("- process_single_question")
