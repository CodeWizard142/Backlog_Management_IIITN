from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

app = Flask(__name__)

# Secret key for session handling
app.secret_key = 'your_secret_key_here'  # Change this to a secure key in production

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backlog_db'

mysql = MySQL(app)

# 👇 Default route is signup page
@app.route('/')
def Signup():
    return render_template('signup.html')

# 👇 Signup form handler
@app.route('/signup', methods=['GET', 'POST'])
def handle_signup():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        email = request.form['email']
        semester = request.form['semester']
        department = request.form['department']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Basic validation
        if not name or not email or not semester or not department or not password:
            return render_template('signup.html', error="Please fill out all fields.")

        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        # Extract student_id from email (before '@')
        student_id = email.split('@')[0]

        # Check if department in email matches the one in the form
        email_dept_match = email.split('@')[0][2:5].upper()
        if email_dept_match != department.upper():
            return render_template('signup.html', error="Department in email does not match the selected department.")

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Debugging: log form data and execution steps
        print(f"Received signup request: {name}, {email}, {semester}, {department}, {student_id}")
        
        try:
            # Establish connection and execute query
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO students (student_id, name, email, semester, department, password_hash) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (student_id, name, email, semester, department, hashed_password)
            )
            mysql.connection.commit()
            cursor.close()

            # Log successful insert
            print(f"Successfully inserted student: {name} with email {email}")
            return redirect(url_for('login'))
        except MySQLdb.IntegrityError as e:
            print(f"IntegrityError: {e}")  # Log error for debugging
            return render_template('signup.html', error="Email already exists. Please use a different one.")
        except MySQLdb.OperationalError as e:
            print(f"OperationalError: {e}")  # Log error for debugging
            return render_template('signup.html', error="Database connection error. Please try again later.")
        except Exception as e:
            print(f"Error: {e}")  # Log generic error for debugging
            return render_template('signup.html', error="An error occurred while saving your data. Please try again.")

    return render_template('signup.html')

# 👇 Login page + logic
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['loggedin'] = True
            session['id'] = user['student_id']  # Corrected session key
            session['name'] = user['name']
            session['email'] = user['email']
            return redirect(url_for('dashboard'))

        return render_template('login.html', error="Invalid email or password.")

    return render_template('login.html')

# 👇 Dashboard route (protected)
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        student_id = session['id']  # Corrected session key
        name = session['name']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
        student_details = cursor.fetchone()

        if student_details:
            return render_template('dashboard.html', student_details=student_details)
        else:
            flash("Student details not found.")
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# 👇 Get backlogs route
@app.route('/my-backlogs', methods=['GET'])
def get_backlogs():
    student_id = session.get('student_id')  # Corrected session key

    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    query = '''
    SELECT course_name, status 
    FROM backlogs 
    WHERE student_id = %s AND status = 'pending'
    '''
    cursor.execute(query, (student_id,))
    backlogs = cursor.fetchall()

    return jsonify(backlogs if backlogs else [])

# 👇 Logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
