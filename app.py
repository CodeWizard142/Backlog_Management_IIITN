from flask import render_template, request, redirect, url_for, flash,Flask
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import MySQLdb.cursors

app = Flask(__name__)

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
        name = request.form['name']
        email = request.form['email']
        semester = request.form['semester']
        department = request.form['department']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Password mismatch check
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match!")

        # Optional: More validation can be added here

        hashed_password = generate_password_hash(password)

        try:
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO students (name, email, semester, department, password_hash) VALUES (%s, %s, %s, %s, %s)",
                (name, email, semester, department, hashed_password)
            )
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('login'))  # Use redirect after success
        except MySQLdb.IntegrityError:
            return render_template('signup.html', error="Email already exists. Please use a different one.")

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
            return "<script>alert('Login successful!'); window.location.href='/dashboard';</script>"

        return "<script>alert('Invalid email or password.'); window.location.href='/login';</script>"

    return render_template('login.html')

# 👇 Simple dashboard route
@app.route('/dashboard')
def dashboard():
    return "<h1>Welcome to your dashboard</h1>"

if __name__ == '__main__':
    app.run(debug=True)
