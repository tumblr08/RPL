import os
import mysql.connector
from mysql.connector import Error

def test_connection():
    try:
        config = {
            'host': os.getenv('MYSQL_HOST') or os.getenv('DB_HOST'),
            'database': os.getenv('MYSQL_DATABASE') or os.getenv('DB_NAME'),
            'user': os.getenv('MYSQL_USER') or os.getenv('DB_USER'),
            'password': os.getenv('MYSQL_PASSWORD') or os.getenv('DB_PASS'),
            'port': int(os.getenv('MYSQL_PORT', os.getenv('DB_PORT', '3306')))
        }
        
        print(f"Testing connection with: {dict(config, password='***')}")
        conn = mysql.connector.connect(**config)
        print("✅ Database connection successful!")
        conn.close()
        
    except Error as e:
        print(f"❌ Database connection failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_connection()