CREATE TABLE students (
  student_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  semester INT,
  department VARCHAR(100),
  password_hash VARCHAR(255)
);

CREATE TABLE admins (
  admin_id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100),
  email VARCHAR(100) UNIQUE,
  password_hash VARCHAR(255),
  role ENUM('superadmin', 'exam_controller', 'faculty') DEFAULT 'faculty'
);

CREATE TABLE subjects (
  subject_id INT PRIMARY KEY AUTO_INCREMENT,
  subject_name VARCHAR(100),
  semester INT,
  department VARCHAR(100)
);

CREATE TABLE backlogs (
  backlog_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  subject_id INT,
  status ENUM('pending', 'cleared') DEFAULT 'pending',
  attempts INT DEFAULT 0,
  grade VARCHAR(5),
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE exam_schedule (
  exam_id INT PRIMARY KEY AUTO_INCREMENT,
  subject_id INT,
  exam_date DATE,
  venue VARCHAR(100),
  semester INT,
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);

CREATE TABLE re_exam_requests (
  request_id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  subject_id INT,
  request_date DATE,
  status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  FOREIGN KEY (student_id) REFERENCES students(student_id),
  FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
);
