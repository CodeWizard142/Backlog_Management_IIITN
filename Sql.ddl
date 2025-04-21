CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL);
CREATE TABLE Admins (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL);
CREATE TABLE Subjects (
    subject_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    semester INT NOT NULL,
    time_slot TIME NOT NULL -- e.g., '08:00:00');
CREATE TABLE Prerequisites (
    subject_id VARCHAR(10),
    prereq_subject_id VARCHAR(10),
    PRIMARY KEY (subject_id, prereq_subject_id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (prereq_subject_id) REFERENCES Subjects(subject_id) ON DELETE CASCADE);
CREATE TABLE Enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_id VARCHAR(10),
    semester INT,
    status ENUM('Enrolled', 'Completed', 'Failed') NOT NULL,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id) ON DELETE CASCADE);
CREATE TABLE Reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_id VARCHAR(10),
    message TEXT,
    status ENUM('Pending', 'Resolved') DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subjects(subject_id) ON DELETE CASCADE);