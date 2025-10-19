import os
import uuid
import time
import logging
from celery import current_task
from celery_config import celery_app
from db_helper import DatabaseHelper
import concurrent.futures
from datetime import datetime

# Import functions from app.py
# Note: We'll import socketio and progress tracking functions within the task functions
# to avoid circular import issues

# Initialize database helper
db_helper = DatabaseHelper()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='tasks.process_pdf_async')
def process_pdf_async(self, pdf_path, name, reg_number, language, phone_number, 
                     file_filename, confirmed=False):
    """
    Asynchronous PDF processing task with status tracking
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(f"Starting PDF processing task {task_id} for user {phone_number}")
    
    # Fetch user and ensure they exist
    current_user = db_helper.get_user_by_phone(phone_number)
    if not current_user:
        logger.error(f"User not found for phone number: {phone_number}")
        return {'status': 'FAILED', 'error': 'User not found'}

    # Insert task record in the database
    task_record = db_helper.create_task_record(
        task_id=task_id,
        user_id=current_user['id'],
        phone_number=phone_number,
        task_type='pdf_processing',
        input_data={
            'pdf_path': pdf_path,
            'name': name,
            'reg_number': reg_number,
            'language': language,
            'file_filename': file_filename
        },
        input_file_path=pdf_path
    )

    if not task_record:
        logger.error(f"Failed to create task record for task {task_id}")
        return {'status': 'FAILED', 'error': 'Failed to create task record'}
    
    try:
        # Update task status to PROCESSING
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=10,
            current_stage='pdf_extraction',
            stage_details='Extracting text from PDF...'
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
            db_helper.update_task_status(task_id, 'FAILED',
                error_message=f"Insufficient credits. Need {total_credits_required}, have {current_user['credits'] if current_user else 0}",
                processing_time_seconds=(time.time() - start_time)
            )
            raise Exception(f"Insufficient credits. Need {total_credits_required}, have {current_user['credits'] if current_user else 0}")
        
        # Update task with question count
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=20,
            current_stage='credit_check',
            stage_details=f'Found {len(questions)} questions, credits required: {total_credits_required}',
            questions_count=len(questions)
        )
        
        # If not confirmed and exceeds 20 questions, require confirmation
        if not confirmed and len(questions) > 20:
            db_helper.update_task_status(task_id, 'PENDING',
                current_stage='awaiting_confirmation',
                stage_details=f'Awaiting user confirmation for {len(questions)} questions'
            )
            return {
                'status': 'CONFIRMATION_REQUIRED',
                'requires_confirmation': True,
                'question_count': len(questions),
                'total_credits_required': total_credits_required,
                'extra_questions': extra_questions,
                'message': f"This PDF contains {len(questions)} questions. Processing will cost {total_credits_required} credits. Do you want to continue?"
            }
        
        # Update status for question processing
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=25,
            current_stage='question_processing',
            stage_details=f'Processing {len(questions)} questions...'
        )
        
        # Process questions in parallel
        solutions_display = []
        screenshots = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_question, q, language) for q in questions]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                sol, scr = future.result()
                solutions_display.append(sol)
                screenshots.append(scr)
                
                # Update progress
                progress = 25 + (i + 1) * 50 // len(questions)
                db_helper.update_task_status(task_id, 'PROCESSING',
                    progress=progress,
                    current_stage='question_processing',
                    stage_details=f'Processed {i + 1}/{len(questions)} questions',
                    questions_solved=len([sol for sol in solutions_display if sol and not sol.startswith("Error")])
                )
        
        # Update status for document generation
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=85,
            current_stage='document_generation',
            stage_details='Generating Word document...'
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
            submission_type='pdf_async'
        )
        
        # Deduct credits
        updated_user = db_helper.deduct_credits_by_count(phone_number, len(questions))
        
        # Update task status to COMPLETED
        db_helper.update_task_status(task_id, 'COMPLETED',
            progress=100,
            current_stage='completed',
            stage_details='Task completed successfully',
            output_file_path=generated_path,
            questions_solved=questions_solved,
            questions_failed=questions_failed,
            credits_used=total_credits_required,
            processing_time_seconds=(time.time() - start_time),
            result_data={
                'file_path': generated_path,
                'questions_count': len(questions),
                'questions_solved': questions_solved,
                'questions_failed': questions_failed,
                'submission_id': submission_record.get('id') if submission_record else None,
                'credits_used': total_credits_required,
                'new_credit_balance': updated_user.get('credits', 0) if updated_user else 0
            }
        )
        
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
        
        # Update task status to FAILED
        db_helper.update_task_status(task_id, 'FAILED',
            error_message=str(e),
            processing_time_seconds=(time.time() - start_time),
            current_stage='failed',
            stage_details=f'Task failed: {str(e)}'
        )
        
        # Record failed submission
        try:
            db_helper.insert_submission(
                phone_number=phone_number,
                pdf_name=file_filename,
                questions_count=0,
                questions_solved=0,
                questions_failed=0,
                failed_questions=[],
                solved=False,
                error_details=f"Async processing failed: {str(e)}",
                processing_time_seconds=(time.time() - start_time),
                submission_type='pdf_async'
            )
        except:
            pass
        
        # Update task state to failure (for Celery)
        current_task.update_state(
            state='FAILURE',
            meta={
                'status': 'Processing failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        raise Exception(f"PDF processing failed: {str(e)}")


@celery_app.task(bind=True, name='tasks.process_manual_questions_async')
def process_manual_questions_async(self, questions_text, name, reg_number, language, 
                                  phone_number, confirmed=False):
    """
    Asynchronous manual questions processing task with status tracking
    """
    task_id = self.request.id
    start_time = time.time()
    
    logger.info(f"Starting manual questions processing task {task_id} for user {phone_number}")
    
    # Fetch user and ensure they exist
    current_user = db_helper.get_user_by_phone(phone_number)
    if not current_user:
        logger.error(f"User not found for phone number: {phone_number}")
        return {'status': 'FAILED', 'error': 'User not found'}

    # Insert task record in the database
    task_record = db_helper.create_task_record(
        task_id=task_id,
        user_id=current_user['id'],
        phone_number=phone_number,
        task_type='manual_questions',
        input_data={
            'questions_text': questions_text,
            'name': name,
            'reg_number': reg_number,
            'language': language
        }
    )

    if not task_record:
        logger.error(f"Failed to create task record for task {task_id}")
        return {'status': 'FAILED', 'error': 'Failed to create task record'}
    
    try:
        # Update task status
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=10,
            current_stage='question_parsing',
            stage_details='Processing questions...'
        )
        
        # Process questions
        questions = split_questions(questions_text) if isinstance(questions_text, str) else questions_text
        
        # Calculate credits required
        base_credits = 1
        extra_questions = max(0, len(questions) - 20)
        total_credits_required = base_credits + extra_questions
        
        # Check credits
        current_user = db_helper.get_user_by_phone(phone_number)
        if not current_user or current_user['credits'] < total_credits_required:
            db_helper.update_task_status(task_id, 'FAILED',
                error_message=f"Insufficient credits. Need {total_credits_required}, have {current_user['credits'] if current_user else 0}",
                processing_time_seconds=(time.time() - start_time)
            )
            raise Exception(f"Insufficient credits. Need {total_credits_required}, have {current_user['credits'] if current_user else 0}")
        
        # Update task with question count
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=20,
            current_stage='credit_check',
            stage_details=f'Found {len(questions)} questions, credits required: {total_credits_required}',
            questions_count=len(questions)
        )
        
        # If not confirmed and exceeds 20 questions, require confirmation
        if not confirmed and len(questions) > 20:
            db_helper.update_task_status(task_id, 'PENDING',
                current_stage='awaiting_confirmation',
                stage_details=f'Awaiting user confirmation for {len(questions)} questions'
            )
            return {
                'status': 'CONFIRMATION_REQUIRED',
                'requires_confirmation': True,
                'question_count': len(questions),
                'total_credits_required': total_credits_required,
                'extra_questions': extra_questions,
                'message': f"You have entered {len(questions)} questions. Processing will cost {total_credits_required} credits. Do you want to continue?"
            }
        
        # Update status for question solving
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=25,
            current_stage='question_solving',
            stage_details=f'Solving {len(questions)} questions...'
        )
        
        # Process questions
        solutions_display = []
        screenshots = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_question, q, language) for q in questions]
            
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                sol, scr = future.result()
                solutions_display.append(sol)
                screenshots.append(scr)
                
                # Update progress
                progress = 25 + (i + 1) * 50 // len(questions)
                db_helper.update_task_status(task_id, 'PROCESSING',
                    progress=progress,
                    current_stage='question_solving',
                    stage_details=f'Solved {i + 1}/{len(questions)} questions',
                    questions_solved=len([sol for sol in solutions_display if sol and not sol.startswith("Error")])
                )
        
        # Update status for document generation
        db_helper.update_task_status(task_id, 'PROCESSING',
            progress=85,
            current_stage='document_generation',
            stage_details='Generating document...'
        )
        
        # Generate document
        output_file = os.path.join('temp', f"manual_solutions_{uuid.uuid4().hex}.docx")
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
            pdf_name='Manual Questions',
            questions_count=len(questions),
            questions_solved=questions_solved,
            questions_failed=questions_failed,
            failed_questions=failed_questions,
            solved=is_fully_solved,
            error_details=None if is_fully_solved else f"{questions_failed} questions failed to solve",
            processing_time_seconds=(time.time() - start_time),
            submission_type='manual_async'
        )
        
        # Deduct credits
        updated_user = db_helper.deduct_credits_by_count(phone_number, len(questions))
        
        # Update task status to COMPLETED
        db_helper.update_task_status(task_id, 'COMPLETED',
            progress=100,
            current_stage='completed',
            stage_details='Task completed successfully',
            output_file_path=generated_path,
            questions_solved=questions_solved,
            questions_failed=questions_failed,
            credits_used=total_credits_required,
            processing_time_seconds=(time.time() - start_time),
            result_data={
                'file_path': generated_path,
                'questions_count': len(questions),
                'questions_solved': questions_solved,
                'questions_failed': questions_failed,
                'submission_id': submission_record.get('id') if submission_record else None,
                'credits_used': total_credits_required,
                'new_credit_balance': updated_user.get('credits', 0) if updated_user else 0
            }
        )
        
        logger.info(f"Manual questions processing task {task_id} completed successfully")
        
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
        logger.error(f"Manual questions processing task {task_id} failed: {str(e)}")
        
        # Update task status to FAILED
        db_helper.update_task_status(task_id, 'FAILED',
            error_message=str(e),
            processing_time_seconds=(time.time() - start_time),
            current_stage='failed',
            stage_details=f'Task failed: {str(e)}'
        )
        
        # Record failed submission
        try:
            db_helper.insert_submission(
                phone_number=phone_number,
                pdf_name='Manual Questions',
                questions_count=0,
                questions_solved=0,
                questions_failed=0,
                failed_questions=[],
                solved=False,
                error_details=f"Async processing failed: {str(e)}",
                processing_time_seconds=(time.time() - start_time),
                submission_type='manual_async'
            )
        except:
            pass
        
        # Update task state to failure (for Celery)
        current_task.update_state(
            state='FAILURE',
            meta={
                'status': 'Processing failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        raise Exception(f"Manual questions processing failed: {str(e)}")


@celery_app.task(bind=True, name='tasks.process_single_question')
def process_single_question(self, question, language='python'):
    """
    Fast processing for single questions
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


# Task monitoring and cleanup
@celery_app.task(name='tasks.cleanup_temp_files')
def cleanup_temp_files():
    """
    Clean up temporary files older than 1 hour
    """
    import glob
    import os
    import time
    
    temp_dir = 'temp'
    current_time = time.time()
    
    for file_path in glob.glob(os.path.join(temp_dir, '*')):
        if os.path.isfile(file_path):
            file_age = current_time - os.path.getctime(file_path)
            if file_age > 3600:  # 1 hour
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up temp file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to clean up {file_path}: {str(e)}")


# Periodic task to clean up temp files
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'tasks.cleanup_temp_files',
        'schedule': crontab(minute=0),  # Run every hour
    },
}
