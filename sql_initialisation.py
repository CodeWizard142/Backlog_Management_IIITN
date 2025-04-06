import mysql.connector
from mysql.connector import Error

try:
    # Connect to MySQL server
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root'  # Change if your MySQL password is different
    )

    if connection.is_connected():
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS backlog_db")
        cursor.execute("USE backlog_db")

        # Students Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            semester INT NOT NULL,
            department VARCHAR(100) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Admins Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS admins (
            admin_id INT PRIMARY KEY AUTO_INCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            role ENUM('superadmin', 'exam_controller', 'faculty') DEFAULT 'faculty',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Subjects Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            subject_id INT PRIMARY KEY AUTO_INCREMENT,
            subject_name VARCHAR(100) NOT NULL,
            semester INT NOT NULL,
            department VARCHAR(100) NOT NULL
        )
        """)

        # Backlogs Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS backlogs (
            backlog_id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT NOT NULL,
            subject_id INT NOT NULL,
            status ENUM('pending', 'cleared') DEFAULT 'pending',
            attempts INT DEFAULT 0,
            grade VARCHAR(5),
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
        """)

        # Exam Schedule Table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_schedule (
            exam_id INT PRIMARY KEY AUTO_INCREMENT,
            subject_id INT NOT NULL,
            exam_date DATE NOT NULL,
            venue VARCHAR(100) NOT NULL,
            semester INT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
        """)

        # Re-Exam Requests Table (Fixed)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS re_exam_requests (
            request_id INT PRIMARY KEY AUTO_INCREMENT,
            student_id INT NOT NULL,
            subject_id INT NOT NULL,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
        )
        """)

        print("Database and tables created successfully!")

except Error as e:
    print(f"Error: {e}")

finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
