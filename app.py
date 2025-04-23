from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import traceback
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backlog_db'

mysql = MySQL(app)

def check_db_connection():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        print("Database connection successful!")
        cursor.close()
    except Exception as e:
        print("Database connection failed:", e)
        traceback.print_exc()

with app.app_context():
    check_db_connection()

@app.route('/')
def Signup():
    return render_template('signup.html')

@app.route('/signup', methods=['GET','POST'])
def handle_signup():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            semester = request.form.get('semester')
            department = request.form.get('department')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')

            if not name or not email or not semester or not department or not password:
                flash("Please fill out all fields.", "error")
                return redirect(url_for('Signup'))

            if password != confirm_password:
                flash("Passwords do not match!", "error")
                return redirect(url_for('Signup'))

            student_id = email.split('@')[0] if '@' in email else ''
            email_match = re.match(r'^bt\d{2}([a-z]{3})\d{3}@iiitn\.ac\.in$', email.lower())
            if email_match:
                email_dept = email_match.group(1).upper()
                if email_dept != department:
                    flash("Department in email does not match the selected department.", "error")
                    return redirect(url_for('Signup'))
            else:
                flash("Invalid email format. Email should be in format: bt20cse001@iiitn.ac.in", "error")
                return redirect(url_for('Signup'))

            hashed_password = generate_password_hash(password)
            cursor = mysql.connection.cursor()
            cursor.execute("SHOW TABLES LIKE 'students'")
            if cursor.fetchone() is None:
                cursor.execute("""
                    CREATE TABLE students (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id VARCHAR(20) UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        semester INT NOT NULL,
                        department VARCHAR(10) NOT NULL,
                        password_hash VARCHAR(255) NOT NULL
                    )
                """)
                mysql.connection.commit()

            cursor.execute(
                "INSERT INTO students (student_id, name, email, semester, department, password_hash) VALUES (%s, %s, %s, %s, %s, %s)",
                (student_id, name, email, semester, department, hashed_password)
            )
            mysql.connection.commit()
            cursor.close()

            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))

        except MySQLdb.IntegrityError as e:
            flash("Email or student ID already exists. Please use a different one.", "error")
            return redirect(url_for('Signup'))
        except Exception as e:
            traceback.print_exc()
            flash("An unexpected error occurred during signup.", "error")
            return redirect(url_for('Signup'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            password = request.form['password']

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password_hash'], password):
                session['loggedin'] = True
                session['id'] = user['student_id']
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for('dashboard'))

            flash("Invalid email or password.", "error")
            return render_template('login.html')

        except Exception as e:
            traceback.print_exc()
            flash("An unexpected error occurred during login.", "error")
            return render_template('login.html')

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        try:
            student_id = session['id']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student_details = cursor.fetchone()
            if student_details:
                return render_template('dashboard.html', student_details=student_details)
        except Exception as e:
            traceback.print_exc()
            flash("Error loading dashboard.", "error")

    flash("Please log in to continue.", "error")
    return redirect(url_for('login'))

@app.route('/my-backlogs', methods=['GET'])
def get_backlogs():
    try:
        student_id = session.get('id')
        if not student_id:
            return jsonify({'error': 'Student ID is required'}), 400

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SHOW TABLES LIKE 'backlogs'")
        if cursor.fetchone() is None:
            cursor.execute("""
                CREATE TABLE backlogs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    student_id VARCHAR(20) NOT NULL,
                    course_name VARCHAR(100) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                )
            """)
            mysql.connection.commit()

        cursor.execute(
            "SELECT course_name, status FROM backlogs WHERE student_id = %s AND status = 'pending'",
            (student_id,)
        )
        backlogs = cursor.fetchall()
        return jsonify(backlogs if backlogs else [])

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': 'Could not retrieve backlogs'}), 500
@app.route('/my-courses', methods=['GET'])
def get_courses():
    try:
        # Check if user is logged in
        student_id = session.get('id')
        if not student_id:
            return jsonify({'error': 'Not logged in'}), 401

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Check if user exists and get their semester
        cursor.execute("SELECT semester, department FROM students WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({'error': 'Student not found'}), 404
            
        semester = student['semester']
        department = student['department']
        
        # Debug - print user information
        print(f"User semester: {semester}, department: {department}")
        
        # Check if courses exist in database for this semester
        cursor.execute("SELECT COUNT(*) as count FROM courses WHERE semester = %s", (semester,))
        count = cursor.fetchone()['count']
        print(f"Found {count} courses for semester {semester}")
        
        # Get the courses for the student's semester
        cursor.execute("SELECT course_id, course_name FROM courses WHERE semester = %s", (semester,))
        courses_data = cursor.fetchall()
        
        # Debug - print raw data
        print(f"Raw courses data: {courses_data}")
        
        # Format the courses data
        courses = [{'id': course['course_id'], 'name': course['course_name']} for course in courses_data]
        
        # Debug - print formatted data
        print(f"Formatted courses: {courses}")
        
        cursor.close()
        return jsonify({'courses': courses, 'debug': {'semester': semester, 'count': count}}), 200
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'An error occurred while fetching courses: {str(e)}'}), 500
    
@app.route('/logout')
def logout():
    try:
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for('login'))
    except Exception as e:
        traceback.print_exc()
        flash("An error occurred during logout.", "error")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)