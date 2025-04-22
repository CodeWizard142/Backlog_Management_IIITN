CREATE DATABASE backlog_db;
USE backlog_db;

-- Students Table
CREATE TABLE students (
    student_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255) UNIQUE,
    semester INT,
    department VARCHAR(10),
    password_hash VARCHAR(255)
);

-- Admins Table
CREATE TABLE admins (
  admin_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('superadmin', 'exam_controller', 'faculty') DEFAULT 'faculty',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subjects Table
CREATE TABLE subjects (
  subject_id INT PRIMARY KEY AUTO_INCREMENT,
  subject_name VARCHAR(100) NOT NULL,
  semester INT NOT NULL,
  department VARCHAR(100) NOT NULL
);

-- Backlogs Table
CREATE TABLE backlogs (
  backlog_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(50) NOT NULL,
  subject_id INT NOT NULL,
  status ENUM('pending', 'cleared') DEFAULT 'pending',
  attempts INT DEFAULT 0,
  grade VARCHAR(5),
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Exam Schedule Table
CREATE TABLE exam_schedule (
  exam_id INT PRIMARY KEY AUTO_INCREMENT,
  subject_id INT NOT NULL,
  exam_date DATE NOT NULL,
  venue VARCHAR(100) NOT NULL,
  semester INT NOT NULL,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

-- Re-Exam Requests Table
CREATE TABLE re_exam_requests (
  request_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id VARCHAR(50) NOT NULL,
  subject_id INT NOT NULL,
  request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);
