import os
import psycopg2
import logging
from dotenv import load_dotenv

def execute_sql_script(sql_script):
    """
    Execute an SQL script on the database
    """
    load_dotenv()
    
    try:
        connection = psycopg2.connect(
            dbname=os.getenv('SUPABASE_DB_NAME', 'postgres'),
            user=os.getenv('SUPABASE_DB_USER', 'postgres'),
            password=os.getenv('SUPABASE_DB_PASSWORD'),
            host=os.getenv('SUPABASE_DB_HOST', 'db.dnyejdazlypnefdqekhr.supabase.co'),
            port=os.getenv('SUPABASE_DB_PORT', '5432')
        )
        cursor = connection.cursor()
        
        with open(sql_script, 'r') as file:
            cursor.execute(file.read())
            connection.commit()
        
        cursor.close()
        connection.close()
        logging.info("SQL script executed successfully.")

    except (Exception, psycopg2.DatabaseError) as db_error:
        logging.error(f"Error executing SQL script: {db_error}")
    

if __name__ == '__main__':
    # Execute both schemas
    print("Creating submissions tables...")
    execute_sql_script('submissions_schema.sql')
    print("Creating payment tables...")
    execute_sql_script('payments_schema.sql')
    print("Database setup complete!")

