import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def migrate_database():
    try:
        # Connect directly to PostgreSQL
        connection = psycopg2.connect(
            dbname='postgres',
            user='postgres.dnyejdazlypnefdqekhr',
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            host='aws-0-ap-south-1.pooler.supabase.com',
            port='6543'
        )
        cursor = connection.cursor()
        
        print('Connected to database successfully')
        
        # Add name column to users table
        cursor.execute('ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(100);')
        print('Added name column to users table')
        
        # Add user_name column to otps table
        cursor.execute('ALTER TABLE otps ADD COLUMN IF NOT EXISTS user_name VARCHAR(100);')
        print('Added user_name column to otps table')
        
        # Update existing users with default names
        cursor.execute("UPDATE users SET name = 'User ' || SUBSTRING(phone_number FROM LENGTH(phone_number) - 3) WHERE name IS NULL;")
        print('Updated users with default names')
        
        # Update the specific test user
        cursor.execute("UPDATE users SET name = 'Tharan' WHERE phone_number = '9311489386';")
        print('Updated test user with name Tharan')
        
        connection.commit()
        cursor.close()
        connection.close()
        print('Migration completed successfully')
        
    except Exception as e:
        print(f'Error: {e}')

if __name__ == '__main__':
    migrate_database()
