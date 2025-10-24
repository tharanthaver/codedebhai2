import os
import logging
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class DatabaseHelper:
    @staticmethod
    def create_user_table():
        """Create users table if it doesn't exist"""
        try:
            # This will be handled through Supabase dashboard/SQL editor
            # We'll create the table manually in Supabase
            pass
        except Exception as e:
            logging.error(f"Error creating user table: {e}")

    @staticmethod
    def get_user_by_phone(phone_number: str):
        """Get user by phone number"""
        try:
            response = supabase.table('users').select('*').eq('phone_number', phone_number).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error getting user by phone: {e}")
            return None

    @staticmethod
    def create_user(phone_number: str, name: str):
        """Create new user with default credits"""
        try:
            user_data = {
                'phone_number': phone_number,
                'name': name,
                'credits': 5,
                'is_priority': False,
                'created_at': datetime.utcnow().isoformat()
            }
            response = supabase.table('users').insert(user_data).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error creating user: {e}")
            return None

    @staticmethod
    def update_user_credits(phone_number: str, credits: int, rolled_over_credits: int = None):
        """Update user credits and optionally track rollover credits"""
        try:
            update_data = {'credits': credits}
            
            # Update rolled_over_credits if provided
            if rolled_over_credits is not None:
                update_data['rolled_over_credits'] = rolled_over_credits
            
            response = supabase.table('users').update(update_data).eq('phone_number', phone_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Error updating credits: {e}")
            return None

    @staticmethod
    def deduct_credit(phone_number: str):
        """Deduct one credit from user"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if user and user['credits'] > 0:
                new_credits = user['credits'] - 1
                return DatabaseHelper.update_user_credits(phone_number, new_credits)
            return None
        except Exception as e:
            logging.error(f"Error deducting credit: {e}")
            return None
    
    @staticmethod
    def deduct_credits_by_count(phone_number: str, question_count: int):
        """Deduct credits based on question count - 1 for up to 20 questions, +1 for each additional question"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                logging.error(f"User not found for phone number: {phone_number}")
                return None
            
            # Calculate credits required: 1 for up to 20 questions, +1 for each additional question
            base_credits = 1
            extra_questions = max(0, question_count - 20)
            total_credits_required = base_credits + extra_questions
            
            if user['credits'] >= total_credits_required:
                new_credits = user['credits'] - total_credits_required
                updated_user = DatabaseHelper.update_user_credits(phone_number, new_credits)
                if updated_user:
                    logging.info(f"{total_credits_required} credits deducted for {phone_number} ({question_count} questions). Remaining credits: {new_credits}")
                    return updated_user
            else:
                logging.warning(f"Insufficient credits for {phone_number} - has {user['credits']}, needs {total_credits_required}")
            return None
        except Exception as e:
            logging.error(f"Error deducting credits by count: {e}")
            return None

    @staticmethod
    def store_otp(phone_number: str, otp_code: str, user_name: str = None):
        """Store OTP for verification"""
        try:
            expiry_time = datetime.utcnow() + timedelta(minutes=int(os.getenv('OTP_EXPIRY_MINUTES', 5)))
            otp_data = {
                'phone_number': phone_number,
                'otp_code': otp_code,
                'expiry_time': expiry_time.isoformat(),
                'is_verified': False,
                'created_at': datetime.utcnow().isoformat()
            }
            
            # Add user_name to OTP data if provided (for new user registration)
            if user_name:
                otp_data['user_name'] = user_name
            
            # Delete any existing OTPs for this phone number
            supabase.table('otps').delete().eq('phone_number', phone_number).execute()
            
            # Insert new OTP
            response = supabase.table('otps').insert(otp_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Error storing OTP: {e}")
            return None

    @staticmethod
    def verify_otp(phone_number: str, otp_code: str):
        """Verify OTP code and return OTP record if valid"""
        try:
            current_time = datetime.utcnow()
            response = supabase.table('otps').select('*').eq('phone_number', phone_number).eq('otp_code', otp_code).eq('is_verified', False).execute()
            
            if response.data:
                otp_record = response.data[0]
                expiry_time = datetime.fromisoformat(otp_record['expiry_time'].replace('Z', '+00:00')).replace(tzinfo=None)
                
                if current_time <= expiry_time:
                    # Mark OTP as verified
                    supabase.table('otps').update({'is_verified': True}).eq('id', otp_record['id']).execute()
                    return otp_record  # Return the full record instead of just True
                else:
                    logging.info("OTP expired")
                    return False
            return False
        except Exception as e:
            logging.error(f"Error verifying OTP: {e}")
            return False

    @staticmethod
    def cleanup_expired_otps():
        """Clean up expired OTPs"""
        try:
            current_time = datetime.utcnow().isoformat()
            supabase.table('otps').delete().lt('expiry_time', current_time).execute()
        except Exception as e:
            logging.error(f"Error cleaning up OTPs: {e}")
    
    @staticmethod
    def insert_submission(phone_number: str, pdf_name: str, questions_count: int, 
                         questions_solved: int, questions_failed: int, failed_questions: list,
                         solved: bool, error_details: str = None, processing_time_seconds: float = None,
                         submission_type: str = 'pdf'):
        """Insert a new submission record with RLS bypass"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                logging.error(f"User not found for phone number: {phone_number}")
                return None
            
            # Get the actual user_id from the users table
            user_id = user.get('id')
            if not user_id:
                logging.error(f"No user ID found for phone number: {phone_number}")
                return None
            
            # Try direct database connection to bypass RLS issues
            try:
                conn = DatabaseHelper._get_direct_connection()
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO submissions (user_id, phone_number, pdf_name, questions_count, 
                                            questions_solved, questions_failed, failed_questions, 
                                            solved, credit_used, submission_type, timestamp, 
                                            error_details, processing_time_seconds)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, user_id, phone_number, pdf_name, questions_count, 
                             questions_solved, questions_failed, solved, timestamp
                """, (user_id, phone_number, pdf_name, questions_count, 
                      questions_solved, questions_failed, failed_questions, 
                      solved, 1 if solved else 0, submission_type, 
                      datetime.utcnow().isoformat(), error_details, processing_time_seconds))
                
                row = cursor.fetchone()
                conn.commit()
                cursor.close()
                conn.close()
                
                if row:
                    submission_record = {
                        'id': row[0],
                        'user_id': row[1],
                        'phone_number': row[2],
                        'pdf_name': row[3],
                        'questions_count': row[4],
                        'questions_solved': row[5],
                        'questions_failed': row[6],
                        'solved': row[7],
                        'timestamp': row[8].isoformat() if row[8] else None
                    }
                    logging.info(f"Submission recorded via direct connection for user {phone_number}: {submission_record['id']}")
                    return submission_record
                    
            except Exception as direct_error:
                logging.warning(f"Direct database insert failed: {direct_error}, trying Supabase client")
                
                # Fallback to original Supabase method
                submission_data = {
                    'user_id': user_id,
                    'phone_number': phone_number,
                    'pdf_name': pdf_name,
                    'questions_count': questions_count,
                    'questions_solved': questions_solved,
                    'questions_failed': questions_failed,
                    'failed_questions': failed_questions,
                    'solved': solved,
                    'credit_used': 1 if solved else 0,
                    'submission_type': submission_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'error_details': error_details,
                    'processing_time_seconds': processing_time_seconds
                }
                
                response = supabase.table('submissions').insert(submission_data).execute()
                if response.data:
                    logging.info(f"Submission recorded via Supabase for user {phone_number}: {response.data[0]['id']}")
                    return response.data[0]
            
            return None
        except Exception as e:
            logging.error(f"Error inserting submission: {e}")
            return None
    
    @staticmethod
    def get_user_submissions(phone_number: str, limit: int = 10):
        """Get user's submission history"""
        try:
            response = supabase.table('submissions').select('*').eq('phone_number', phone_number).order('timestamp', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Error getting user submissions: {e}")
            return []
    
    @staticmethod
    def get_user_stats(phone_number: str):
        """Get user statistics from submissions"""
        try:
            response = supabase.table('user_submission_stats').select('*').eq('phone_number', phone_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Error getting user stats: {e}")
            return None
    
    # =================== PAYMENT METHODS ===================
    
    @staticmethod
    def _get_direct_connection():
        """Get direct PostgreSQL connection to bypass RLS"""
        import psycopg2
        
        # Prefer pooled transaction URL if present (production)
        connection_string = os.getenv("SUPABASE_POOLER_TRANSACTION_URL")
        if connection_string:
            try:
                logging.info("🔗 Attempting pooled connection...")
                return psycopg2.connect(connection_string)
            except Exception as e:
                logging.warning(f"⚠️ Pooled connection failed: {e}")

        # Fallback: direct connection via discrete env vars
        host = os.getenv("SUPABASE_DB_HOST")
        database = os.getenv("SUPABASE_DB_NAME", "postgres")
        user = os.getenv("SUPABASE_DB_USER", "postgres")
        password = os.getenv("SUPABASE_DB_PASSWORD")
        port = int(os.getenv("SUPABASE_DB_PORT", "5432"))

        if not host or not password:
            raise RuntimeError("❌ Missing SUPABASE_DB_HOST or SUPABASE_DB_PASSWORD")

        try:
            logging.info(f"🔗 Attempting direct connection to {host}:{port}")
            return psycopg2.connect(
                host=host,
                database=database,
                user=user,
                password=password,
                port=port,
                connect_timeout=10,
                sslmode='require'
            )
        except Exception as e:
            logging.error(f"❌ Direct connection failed: {e}")
            # Try using Supabase client as final fallback
            logging.info("🔄 Falling back to Supabase client for database operations")
            raise RuntimeError(f"Database connection failed: {e}")
    
    @staticmethod
    def get_payment_plans():
        """Get all active payment plans"""
        try:
            # Use direct connection to bypass RLS
            conn = DatabaseHelper._get_direct_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, plan_name, plan_type, amount, credits, is_priority, description, is_active, created_at, updated_at
                FROM payment_plans 
                WHERE is_active = true 
                ORDER BY amount
            """)
            
            rows = cursor.fetchall()
            plans = []
            for row in rows:
                plans.append({
                    'id': row[0],
                    'plan_name': row[1],
                    'plan_type': row[2],
                    'amount': row[3],
                    'credits': row[4],
                    'is_priority': row[5],
                    'description': row[6],
                    'is_active': row[7],
                    'created_at': row[8].isoformat() if row[8] else None,
                    'updated_at': row[9].isoformat() if row[9] else None
                })
            
            cursor.close()
            conn.close()
            
            return plans
        except Exception as e:
            logging.error(f"Error getting payment plans: {e}")
            return []
    
    @staticmethod
    def get_payment_plan(plan_type: str):
        """Get specific payment plan by type"""
        try:
            # Use direct connection to bypass RLS
            conn = DatabaseHelper._get_direct_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, plan_name, plan_type, amount, credits, is_priority, description, is_active, created_at, updated_at
                FROM payment_plans 
                WHERE plan_type = %s AND is_active = true
            """, (plan_type,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'plan_name': row[1],
                    'plan_type': row[2],
                    'amount': row[3],
                    'credits': row[4],
                    'is_priority': row[5],
                    'description': row[6],
                    'is_active': row[7],
                    'created_at': row[8].isoformat() if row[8] else None,
                    'updated_at': row[9].isoformat() if row[9] else None
                }
            return None
        except Exception as e:
            logging.error(f"Error getting payment plan {plan_type}: {e}")
            return None
    
    @staticmethod
    def create_payment_plan(plan_name: str, plan_type: str, amount: int, credits: int, 
                          is_priority: bool = False, description: str = None):
        """Create a new payment plan"""
        try:
            plan_data = {
                'plan_name': plan_name,
                'plan_type': plan_type,
                'amount': amount,
                'credits': credits,
                'is_priority': is_priority,
                'description': description,
                'is_active': True,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('payment_plans').insert(plan_data).execute()
            if response.data:
                logging.info(f"Payment plan created: {plan_type}")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error creating payment plan: {e}")
            return None
    
    @staticmethod
    def get_or_create_payment_plan(plan_type: str):
        """Get payment plan or create it with default values based on plan type"""
        # Try to get existing plan first
        existing_plan = DatabaseHelper.get_payment_plan(plan_type)
        if existing_plan:
            return existing_plan
        
        # Define default plans
        plan_configs = {
            'starter': {
                'plan_name': 'Starter Plan',
                'amount': 9900,  # ₹99 in paise
                'credits': 10,
                'is_priority': False,
                'description': '₹99 → 10 credits - Entry-level for new users',
                'badge': 'New Entry',
                'features': [
                    '✅ 1 credit = 1 solved pdf (max 20 questions)',
                    '✅ Entry-level for new users',
                    '✅ Ideal for light users',
                    '✅ Perfect for trying us out!',
                    '✅ Test drive our service'
                ]
            },
            'monthly': {
                'plan_name': 'Monthly Saver',
                'amount': 29900,  # ₹299 in paise
                'credits': 50,
                'is_priority': False,
                'description': '₹299 → 50 credits - Best value for regular users',
                'badge': 'Best Value',
                'is_featured': True,
                'savings': 'Save 33% per question!',
                'features': [
                    '✅ 50 pdf Solutions',
                    '✅ Flexibility & reliability',
                    '✅ Solve more when needed',
                    '✅ Great for regular assignments',
                    '✅ Perfect for semester workload',
                    '✅ Most Popular Among students'
                ]
            },
            'power': {
                'plan_name': 'Power Plan',
                'amount': 79900,  # ₹799 in paise
                'credits': 150,  # Fixed: was 110, now 150
                'is_priority': True,
                'description': '₹799 → 150 credits + Priority Access - Maximum value for consistent users',
                'badge': '3 Months Access',
                'savings': 'Save 45% vs Starter!',
                'features': [
                    '✅ 150 pdf solved',
                    '✅ Valid for 3 months',
                    '✅ Priority solving queue',
                    '✅ Perfect for exam rush & semester load',
                    '✅ Maximum value for consistent users'
                ]
            }
        }
        
        if plan_type in plan_configs:
            config = plan_configs[plan_type]
            return DatabaseHelper.create_payment_plan(
                plan_name=config['plan_name'],
                plan_type=plan_type,
                amount=config['amount'],
                credits=config['credits'],
                is_priority=config['is_priority'],
                description=config['description']
            )
        
        logging.error(f"Unknown plan type: {plan_type}")
        return None
    
    @staticmethod
    def create_payment_record(user_id: int, phone_number: str, gateway_order_id: str, 
                            gateway_payment_id: str, amount: int, credits_added: int, 
                            plan_type: str, payment_status: str = 'pending', gateway_type: str = 'cashfree'):
        """Create a payment record with enhanced logging and fallback to Supabase client"""
        try:
            # Try direct connection first
            conn = DatabaseHelper._get_direct_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO payments (user_id, phone_number, gateway_order_id, gateway_payment_id, 
                                    gateway_type, amount, credits_added, plan_type, payment_status, webhook_received)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id, user_id, phone_number, gateway_order_id, gateway_payment_id, 
                         gateway_type, amount, credits_added, plan_type, payment_status, webhook_received, created_at, updated_at
            """, (user_id, phone_number, gateway_order_id, gateway_payment_id, 
                  gateway_type, amount, credits_added, plan_type, payment_status, False))
            
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if row:
                payment_record = {
                    'id': row[0],
                    'user_id': row[1],
                    'phone_number': row[2],
                    'gateway_order_id': row[3],
                    'gateway_payment_id': row[4],
                    'gateway_type': row[5],
                    'amount': row[6],
                    'credits_added': row[7],
                    'plan_type': row[8],
                    'payment_status': row[9],
                    'webhook_received': row[10],
                    'created_at': row[11].isoformat() if row[11] else None,
                    'updated_at': row[12].isoformat() if row[12] else None
                }
                logging.info(f"💳 Payment record created: ID {payment_record['id']}, Order: {gateway_order_id}, Amount: ₹{amount/100}, Credits: {credits_added}")
                return payment_record
            return None
            
        except Exception as e:
            logging.warning(f"⚠️ Direct connection failed for payment record: {e}")
            # Fallback to Supabase client
            try:
                logging.info("🔄 Using Supabase client fallback for payment record")
                payment_data = {
                    'user_id': user_id,
                    'phone_number': phone_number,
                    'gateway_order_id': gateway_order_id,
                    'gateway_payment_id': gateway_payment_id,
                    'gateway_type': gateway_type,
                    'amount': amount,
                    'credits_added': credits_added,
                    'plan_type': plan_type,
                    'payment_status': payment_status,
                    'webhook_received': False,
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                response = supabase.table('payments').insert(payment_data).execute()
                if response.data:
                    payment_record = response.data[0]
                    logging.info(f"💳 Payment record created via Supabase: ID {payment_record['id']}, Order: {gateway_order_id}")
                    return payment_record
                return None
                
            except Exception as fallback_error:
                logging.error(f"❌ Error creating payment record (both methods failed): {fallback_error}")
                return None
    
    @staticmethod
    def update_payment_status(gateway_order_id: str, status: str, gateway_payment_id: str = None):
        """Update payment status using order ID with enhanced logging"""
        try:
            # Use direct connection for consistency
            conn = DatabaseHelper._get_direct_connection()
            cursor = conn.cursor()
            
            # Build update query
            if gateway_payment_id:
                cursor.execute("""
                    UPDATE payments 
                    SET payment_status = %s, gateway_payment_id = %s, webhook_received = %s, updated_at = NOW()
                    WHERE gateway_order_id = %s
                    RETURNING id, user_id, phone_number, gateway_order_id, gateway_payment_id, 
                             amount, credits_added, plan_type, payment_status, created_at, updated_at
                """, (status, gateway_payment_id, True, gateway_order_id))
            else:
                cursor.execute("""
                    UPDATE payments 
                    SET payment_status = %s, webhook_received = %s, updated_at = NOW()
                    WHERE gateway_order_id = %s
                    RETURNING id, user_id, phone_number, gateway_order_id, gateway_payment_id, 
                             amount, credits_added, plan_type, payment_status, created_at, updated_at
                """, (status, True, gateway_order_id))
            
            row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if row:
                payment_record = {
                    'id': row[0],
                    'user_id': row[1],
                    'phone_number': row[2],
                    'gateway_order_id': row[3],
                    'gateway_payment_id': row[4],
                    'amount': row[5],
                    'credits_added': row[6],
                    'plan_type': row[7],
                    'payment_status': row[8],
                    'created_at': row[9].isoformat() if row[9] else None,
                    'updated_at': row[10].isoformat() if row[10] else None
                }
                logging.info(f"✅ Payment status updated: Order {gateway_order_id} → {status} (Payment ID: {gateway_payment_id})")
                return payment_record
            else:
                logging.warning(f"⚠️ No payment record found to update for order: {gateway_order_id}")
                return None
        except Exception as e:
            logging.error(f"❌ Error updating payment status: {e}")
            return None
    
    @staticmethod
    def get_payment_by_gateway_id(gateway_order_id: str):
        """Get payment record by gateway order ID"""
        try:
            # Use direct connection to bypass RLS
            conn = DatabaseHelper._get_direct_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, user_id, phone_number, gateway_order_id, gateway_payment_id, 
                       gateway_type, amount, credits_added, plan_type, payment_status, created_at, updated_at
                FROM payments 
                WHERE gateway_order_id = %s
            """, (gateway_order_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'user_id': row[1],
                    'phone_number': row[2],
                    'gateway_order_id': row[3],
                    'gateway_payment_id': row[4],
                    'gateway_type': row[5],
                    'amount': row[6],
                    'credits_added': row[7],
                    'plan_type': row[8],
                    'payment_status': row[9],
                    'created_at': row[10].isoformat() if row[10] else None,
                    'updated_at': row[11].isoformat() if row[11] else None
                }
            return None
        except Exception as e:
            logging.error(f"Error getting payment by gateway ID: {e}")
            return None
    
    @staticmethod
    def carry_over_credits(phone_number: str, previous_credits: int, purchase_amount: int):
        """Carry over remaining credits if re-qualified by a new purchase."""
        try:
            if purchase_amount in (299, 799):
                user = DatabaseHelper.get_user_by_phone(phone_number)
                if user:
                    new_credits = user['credits'] + previous_credits
                    return DatabaseHelper.update_user_credits(phone_number, new_credits)
            return None
        except Exception as e:
            logging.error(f"Error carrying over credits: {e}")
            return None

    @staticmethod
    def add_credits_to_user(phone_number: str, credits: int, set_priority: bool = False):
        """Add credits to user account and optionally set priority status"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                logging.error(f"User not found for phone number: {phone_number}")
                return None
            
            # Add credits to existing balance - NO BONUS CREDITS
            new_credits = user['credits'] + credits
            update_data = {'credits': new_credits}
            
            if set_priority:
                update_data['is_priority'] = True
            
            response = supabase.table('users').update(update_data).eq('phone_number', phone_number).execute()
            
            if response.data:
                logging.info(f"Credits added to user {phone_number}: +{credits} credits, total: {new_credits}")
                if set_priority:
                    logging.info(f"User {phone_number} set to priority status")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error adding credits to user: {e}")
            return None
    
    @staticmethod
    def get_user_payments(phone_number: str, limit: int = 10):
        """Get user's payment history"""
        try:
            response = supabase.table('payments').select('*').eq('phone_number', phone_number).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Error getting user payments: {e}")
            return []
    
    @staticmethod
    def get_user_payment_stats(phone_number: str):
        """Get user payment statistics"""
        try:
            response = supabase.table('user_payment_stats').select('*').eq('phone_number', phone_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Error getting user payment stats: {e}")
            return None
    
    # =================== TASK TRACKING METHODS ===================
    
    @staticmethod
    def create_task_record(task_id: str, user_id: int, phone_number: str, task_type: str, 
                          input_data: dict = None, input_file_path: str = None):
        """Create a new task record"""
        try:
            task_data = {
                'task_id': task_id,
                'user_id': user_id,
                'phone_number': phone_number,
                'task_type': task_type,
                'task_status': 'PENDING',
                'task_progress': 0,
                'input_data': input_data,
                'input_file_path': input_file_path,
                'created_at': datetime.utcnow().isoformat()
            }
            
            response = supabase.table('tasks').insert(task_data).execute()
            if response.data:
                logging.info(f"Task record created: {task_id}")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error creating task record: {e}")
            return None
    
    @staticmethod
    def update_task_status(task_id: str, status: str, progress: int = None, 
                          current_stage: str = None, stage_details: str = None,
                          questions_count: int = None, questions_solved: int = None,
                          questions_failed: int = None, credits_used: int = None,
                          processing_time_seconds: float = None, error_message: str = None,
                          result_data: dict = None, output_file_path: str = None):
        """Update task status and progress"""
        try:
            update_data = {
                'task_status': status,
                'updated_at': datetime.utcnow().isoformat()
            }
            
            if progress is not None:
                update_data['task_progress'] = progress
            if current_stage is not None:
                update_data['current_stage'] = current_stage
            if stage_details is not None:
                update_data['stage_details'] = stage_details
            if questions_count is not None:
                update_data['questions_count'] = questions_count
            if questions_solved is not None:
                update_data['questions_solved'] = questions_solved
            if questions_failed is not None:
                update_data['questions_failed'] = questions_failed
            if credits_used is not None:
                update_data['credits_used'] = credits_used
            if processing_time_seconds is not None:
                update_data['processing_time_seconds'] = processing_time_seconds
            if error_message is not None:
                update_data['error_message'] = error_message
            if result_data is not None:
                update_data['result_data'] = result_data
            if output_file_path is not None:
                update_data['output_file_path'] = output_file_path
            
            response = supabase.table('tasks').update(update_data).eq('task_id', task_id).execute()
            
            if response.data:
                logging.info(f"Task status updated for {task_id}: {status}")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error updating task status: {e}")
            return None
    
    @staticmethod
    def get_task_by_id(task_id: str):
        """Get task record by task ID"""
        try:
            response = supabase.table('tasks').select('*').eq('task_id', task_id).execute()
            if response.data:
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error getting task by ID: {e}")
            return None
    
    @staticmethod
    def get_user_tasks(phone_number: str, limit: int = 10):
        """Get user's task history"""
        try:
            response = supabase.table('tasks').select('*').eq('phone_number', phone_number).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Error getting user tasks: {e}")
            return []
    
    @staticmethod
    def get_active_tasks(limit: int = 50):
        """Get all active tasks (PENDING or PROCESSING)"""
        try:
            response = supabase.table('tasks').select('*').in_('task_status', ['PENDING', 'PROCESSING']).order('created_at', desc=True).limit(limit).execute()
            return response.data if response.data else []
        except Exception as e:
            logging.error(f"Error getting active tasks: {e}")
            return []
    
    @staticmethod
    def get_user_task_stats(phone_number: str):
        """Get user task statistics"""
        try:
            response = supabase.table('user_task_stats').select('*').eq('phone_number', phone_number).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logging.error(f"Error getting user task stats: {e}")
            return None
    
    @staticmethod
    def cleanup_old_tasks(days_old: int = 30):
        """Clean up old completed tasks"""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days_old)).isoformat()
            response = supabase.table('tasks').delete().in_('task_status', ['COMPLETED', 'FAILED']).lt('completed_at', cutoff_date).execute()
            deleted_count = len(response.data) if response.data else 0
            logging.info(f"Cleaned up {deleted_count} old tasks")
            return deleted_count
        except Exception as e:
            logging.error(f"Error cleaning up old tasks: {e}")
            return 0
    
    # =================== ROLLOVER CREDIT METHODS ===================
    
    @staticmethod
    def set_rollover_credits(phone_number: str, rollover_credits: int):
        """Set rollover credits for a user (used during monthly rollover)"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                logging.error(f"User not found for phone number: {phone_number}")
                return None
            
            # Update rollover credits and total credits
            response = supabase.table('users').update({
                'credits': rollover_credits,
                'rolled_over_credits': rollover_credits
            }).eq('phone_number', phone_number).execute()
            
            if response.data:
                logging.info(f"Rollover credits set for {phone_number}: {rollover_credits} credits")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error setting rollover credits: {e}")
            return None
    
    @staticmethod
    def add_credits_with_rollover_tracking(phone_number: str, new_credits: int, set_priority: bool = False):
        """Add credits to user account while preserving rollover tracking"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                logging.error(f"User not found for phone number: {phone_number}")
                return None
            
            # Get current rollover credits (preserved)
            current_rollover = user.get('rolled_over_credits', 0)
            
            # Add new credits to existing balance
            new_total_credits = user['credits'] + new_credits
            
            update_data = {
                'credits': new_total_credits,
                'rolled_over_credits': current_rollover  # Keep rollover credits unchanged
            }
            
            if set_priority:
                update_data['is_priority'] = True
            
            response = supabase.table('users').update(update_data).eq('phone_number', phone_number).execute()
            
            if response.data:
                logging.info(f"Credits added to user {phone_number}: +{new_credits} credits, total: {new_total_credits}, rollover: {current_rollover}")
                if set_priority:
                    logging.info(f"User {phone_number} set to priority status")
                return response.data[0]
            return None
        except Exception as e:
            logging.error(f"Error adding credits with rollover tracking: {e}")
            return None
    
    @staticmethod
    def get_user_credit_breakdown(phone_number: str):
        """Get detailed credit breakdown for a user"""
        try:
            user = DatabaseHelper.get_user_by_phone(phone_number)
            if not user:
                return None
            
            total_credits = user.get('credits', 0)
            rollover_credits = user.get('rolled_over_credits', 0)
            current_month_credits = total_credits - rollover_credits
            
            return {
                'phone_number': phone_number,
                'name': user.get('name', 'Unknown'),
                'total_credits': total_credits,
                'rolled_over_credits': rollover_credits,
                'current_month_credits': current_month_credits,
                'is_priority': user.get('is_priority', False),
                'rollover_status': 'Has Rollover' if rollover_credits > 0 else 'No Rollover'
            }
        except Exception as e:
            logging.error(f"Error getting credit breakdown: {e}")
            return None
    
    @staticmethod
    def get_all_users_with_rollover_info():
        """Get all users with their rollover credit information"""
        try:
            response = supabase.table('users').select('*').gt('credits', 0).execute()
            users = response.data if response.data else []
            
            rollover_info = []
            for user in users:
                total_credits = user.get('credits', 0)
                rollover_credits = user.get('rolled_over_credits', 0)
                
                rollover_info.append({
                    'phone_number': user['phone_number'],
                    'name': user.get('name', 'Unknown'),
                    'total_credits': total_credits,
                    'rolled_over_credits': rollover_credits,
                    'current_month_credits': total_credits - rollover_credits,
                    'is_priority': user.get('is_priority', False),
                    'created_at': user.get('created_at')
                })
            
            return rollover_info
        except Exception as e:
            logging.error(f"Error getting users with rollover info: {e}")
            return []
    
    @staticmethod
    def get_rollover_summary_stats():
        """Get summary statistics for rollover credits"""
        try:
            response = supabase.table('users').select('credits, rolled_over_credits').gt('credits', 0).execute()
            users = response.data if response.data else []
            
            total_users = len(users)
            total_credits = sum(user.get('credits', 0) for user in users)
            total_rollover_credits = sum(user.get('rolled_over_credits', 0) for user in users)
            total_current_month_credits = total_credits - total_rollover_credits
            users_with_rollover = sum(1 for user in users if user.get('rolled_over_credits', 0) > 0)
            
            return {
                'total_users': total_users,
                'total_credits': total_credits,
                'total_rolled_over_credits': total_rollover_credits,
                'total_current_month_credits': total_current_month_credits,
                'users_with_rollover': users_with_rollover,
                'avg_rollover_per_user': round(total_rollover_credits / total_users, 2) if total_users > 0 else 0,
                'max_rollover_credits': max((user.get('rolled_over_credits', 0) for user in users), default=0)
            }
        except Exception as e:
            logging.error(f"Error getting rollover summary stats: {e}")
            return None
