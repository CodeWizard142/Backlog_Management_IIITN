from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
import traceback

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Use a strong key in production

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backlog_db'

mysql = MySQL(app)

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

            student_id = email.split('@')[0]
            email_dept_match = student_id[2:5].strip().upper()
            department = department.strip().upper()

            if email_dept_match != department:
                flash("Department in email does not match the selected department.", "error")
                return redirect(url_for('Signup'))

            hashed_password = generate_password_hash(password)

            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO students (student_id, name, email, semester, department, password_hash) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (student_id, name, email, semester, department, hashed_password)
            )
            mysql.connection.commit()
            cursor.close()

            flash("Signup successful! Please log in.", "success")
            return redirect(url_for('login'))

        except MySQLdb.IntegrityError as e:
            print("MySQL Integrity Error:", e)
            traceback.print_exc()
            flash("Email already exists. Please use a different one.", "error")
            return redirect(url_for('Signup'))
        except Exception as e:
            print("Signup Error:", e)
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
            print("Login Error:", e)
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
            print("Dashboard Error:", e)
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
        cursor.execute(
            "SELECT course_name, status FROM backlogs WHERE student_id = %s AND status = 'pending'",
            (student_id,)
        )
        backlogs = cursor.fetchall()
        return jsonify(backlogs if backlogs else [])

    except Exception as e:
        print("Backlogs Fetch Error:", e)
        traceback.print_exc()
        return jsonify({'error': 'Could not retrieve backlogs'}), 500

@app.route('/logout')
def logout():
    try:
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for('login'))
    except Exception as e:
        print("Logout Error:", e)
        traceback.print_exc()
        flash("An error occurred during logout.", "error")
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
