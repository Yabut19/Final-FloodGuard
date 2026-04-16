from utils.db import get_db
import mysql.connector

def check_structure_and_data():
    try:
        db = get_db()
        cursor = db.cursor()
        
        for table in ['users', 'admins']:
            print(f"\n--- Checking Table: {table} ---")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
                
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"Total Records: {count}")
            
            if count > 0:
                cursor.execute(f"SELECT * FROM {table} LIMIT 1")
                print(f"Sample Row: {cursor.fetchone()}")

        cursor.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_structure_and_data()
