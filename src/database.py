import sqlite3
import time

DB_NAME = "waste_detection.db"

def init_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class TEXT,
        bin TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_to_database(waste_type,bin_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO detections (class, bin, timestamp) VALUES (?, ?, ?)",
                   (waste_type, bin_name, timestamp))

    conn.commit()
    conn.close()