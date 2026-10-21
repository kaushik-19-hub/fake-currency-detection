import sqlite3
from werkzeug.security import generate_password_hash

DATABASE_NAME = "database.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # =====================================
    # Create users table
    # =====================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    """)

    # =====================================
    # Create detection history table
    # =====================================
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detection_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            image_path TEXT NOT NULL,
            result TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # =====================================
    # Check if admin exists
    # =====================================
    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        ("admin",)
    )
    admin_exists = cursor.fetchone()

    # =====================================
    # Create default admin account
    # =====================================
    if admin_exists is None:
        hashed_password = generate_password_hash("admin123")

        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (
            "admin",
            "admin@gmail.com",
            hashed_password,
            "admin"
        ))

        print("Admin account created successfully.")
        print("Username: admin")
        print("Password: admin123")
    else:
        print("Admin account already exists.")

    conn.commit()
    conn.close()

    print("Database initialized successfully.")


if __name__ == "__main__":
    create_database()