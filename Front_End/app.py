from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash


app = Flask(__name__)

# MySQL config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'backlog_db'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')  # Assuming login.html is in /templates

# Example login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = request.form['email']
    password = request.form['password']

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM students WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password_hash'], password):
        return jsonify({'message': 'Login successful', 'student_id': user['student_id']})
    return jsonify({'message': 'Invalid email or password'}), 401

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        semester = request.form['semester']
        department = request.form['department']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO students (name, email, semester, department, password_hash) VALUES (%s, %s, %s, %s, %s)",
                           (name, email, semester, department, hashed_password))
            mysql.connection.commit()
            cursor.close()
            flash("Signup successful! Please login.", "success")
            return redirect(url_for('login'))  # Redirect to login page
        except MySQLdb.IntegrityError as e:
            flash("Email already exists. Please use a different one.", "warning")
            return redirect(url_for('signup'))

    return render_template('Signup.html')  # Serve the HTML page