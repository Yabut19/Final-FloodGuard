from config import Config
import mysql.connector

def create_iot_readings_table():
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cursor = conn.cursor()

        # Check if iot_readings table exists
        cursor.execute("SHOW TABLES LIKE 'iot_readings'")
        result = cursor.fetchone()

        if not result:
            print("Creating iot_readings table...")
            cursor.execute("""
                CREATE TABLE iot_readings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    sensor_id VARCHAR(50) NOT NULL,
                    raw_distance DECIMAL(5,2),
                    flood_level DECIMAL(5,2),
                    status VARCHAR(20),
                    latitude DECIMAL(10,8),
                    longitude DECIMAL(11,8),
                    maps_url VARCHAR(500),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_sensor_id (sensor_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            conn.commit()
            print("iot_readings table created successfully.")
        else:
            print("iot_readings table already exists.")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Failed to create iot_readings table: {e}")

if __name__ == "__main__":
    create_iot_readings_table()