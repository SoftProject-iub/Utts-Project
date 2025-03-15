from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import mysql.connector
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Folder to store uploaded images

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MySQL Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bus_tracking_system'
}

# Helper function to get database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Home Route
@app.route('/')
def home():
    if 'username' in session and 'user_id' in session:  # Check if 'username' and 'user_id' are in session
        user = session['username']
        user_id = session['user_id']  # Retrieve user_id from session

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Fetch buses
            cursor.execute('SELECT * FROM buses ORDER BY id DESC')
            buses = cursor.fetchall()  # Fetch all rows from the first query

            # Fetch student_info for the logged-in user
            cursor.execute('SELECT * FROM student_info WHERE user_id = %s', (user_id,))
            student_info = cursor.fetchone()  # Fetch the student info for the logged-in user

            # Fetch notifications
            cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC')
            notifications = cursor.fetchall()  # Fetch all rows from the second query

            return render_template(
                'dashboard.html',
                user=user,
                buses=buses,
                student_info=student_info,  # Pass student_info to the template
                notifications=notifications
            )

        finally:
            cursor.close()
            conn.close()

    return redirect(url_for('login'))  # Redirect to login if user is not logged in

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            # Check if the user exists in the database
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()

            if user:
                # Store username and user_id in the session
                session['username'] = user['username']
                session['user_id'] = user['id']  # Store user_id in session
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid username or password', 'error')
        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('signup'))
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()
            flash('Signup successful! Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username or email already exists', 'error')
        finally:
            cursor.close()
            conn.close()
    return render_template('signup.html')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Admin Panel Route
# Admin Panel Route
@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT COUNT(id) FROM buses')
        buses = cursor.fetchone()

        cursor.execute('SELECT COUNT(id) FROM users')
        users = cursor.fetchone()

        cursor.execute('SELECT COUNT(id) FROM routes')
        routes = cursor.fetchone()
        print(buses)
        print(users)
        print(routes)

        return render_template('admin.html', buses=buses[0], users=users[0], routes=routes[0])
    finally:
        cursor.close()
        conn.close()

# Add Bus Route
@app.route('/admin/bus_management', methods=['GET', 'POST'])
def bus_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM buses')
        buses = cursor.fetchall()
        return render_template('buses.html',buses=buses)
    finally:
        cursor.close()
        conn.close()

# Add Route Route
@app.route('/admin/route_management', methods=['GET', 'POST'])
def route_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM routes')
        routes = cursor.fetchall()
        return render_template('routes.html', routes=routes, datetime=datetime)
    finally:
        cursor.close()
        conn.close()

# User management
@app.route('/admin/user_management')
def user_management():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        print(users)
        return render_template('users.html', users=users)
    finally:
        cursor.close()
        conn.close()


# Schedule Route
@app.route('/schedule')
def schedule():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM schedules')
        bus_schedules = cursor.fetchall()
        return render_template('schedule.html', bus_schedules=bus_schedules, datetime=datetime)
    finally:
        cursor.close()
        conn.close()

# Map Route
@app.route('/map')
def map():
    return render_template('map.html')


# Contact Route
@app.route('/contact')
def contact():
    return render_template('contact.html')

# Profile Route
@app.route('/profile')
def student_info():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM student_info WHERE user_id = %s', (user_id,))
            student_info = cursor.fetchone()
            return render_template('student_info.html', student_info=student_info)
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))



# Add Bus Route
@app.route('/admin/add_bus', methods=['GET', 'POST'])
def add_bus():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        route = request.form['route']
        status = request.form['status']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO buses (name, route, status) VALUES (%s, %s, %s)', (name, route, status))
            conn.commit()
            flash('Bus added successfully!', 'success')
            return redirect(url_for('admin'))
        finally:
            cursor.close()
            conn.close()
    return render_template('add_bus.html')

# # Send Notification
# @app.route('/admin/send_notification', methods=['GET', 'POST'])
# def send_notification():
#     if 'username' not in session:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         title = request.form['name']
#         message = request.form['route']
#         status = request.form['status']
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute('INSERT INTO notifications (title, message, type) VALUES (%s, %s, %s)', (title, message, status))
#             conn.commit()
#             flash('Notification added successfully!', 'success')
#             return redirect(url_for('admin'))
#         finally:
#             cursor.close()
#             conn.close()
#     return render_template('send_notification.html')

# Add Route Route
@app.route('/admin/add_route', methods=['GET', 'POST'])
def add_route():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        name = request.form['name']
        stops = request.form['stops']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO routes (name, stops) VALUES (%s, %s)', (name, stops))
            conn.commit()
            flash('Route added successfully!', 'success')
            return redirect(url_for('admin'))
        finally:
            cursor.close()
            conn.close()
    return render_template('add_route.html')


# Fetch Notifications Route
@app.route('/admin/notification_management')
def notification_management():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 3')
        notifications = cursor.fetchall()
        return render_template('notifications.html', notifications=notifications)
    finally:
        cursor.close()
        conn.close()

# Send Notifications Route
@app.route('/admin/send_notification', methods=['GET', 'POST'])
def send_notification():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        message = request.form['message']
        notification_type = request.form['type']  # Avoid using 'type' as a variable name
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO notifications (title, message, type) VALUES (%s, %s, %s)',
                           (title, message, notification_type))
            conn.commit()
            flash('Notification sent successfully!', 'success')
            return redirect(url_for('notification_management'))
        finally:
            cursor.close()
            conn.close()

    # Render the form template for GET requests
    return render_template('send_notification.html')













# Feedback Submission Route
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO feedback (name, email, message) VALUES (%s, %s, %s)', (name, email, message))
            conn.commit()
            flash('Thank you for your feedback!', 'success')
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'error')
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('home'))  # Redirect to the home page or any other page

# Feedback Management Route

@app.route('/admin/feedback_management')
def feedback_management():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get search query
    search_query = request.args.get('search', '')

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of feedback items per page

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Base query
        query = 'SELECT * FROM feedback'
        if search_query:
            query += ' WHERE name LIKE %s OR email LIKE %s'
            search_pattern = f'%{search_query}%'
            cursor.execute(query, (search_pattern, search_pattern))
        else:
            cursor.execute(query)

        # Fetch all feedback for pagination
        feedbacks = cursor.fetchall()
        return render_template('feedback_management.html', feedbacks=feedbacks)
    finally:
        cursor.close()
        conn.close()

# Route to update or add student information
@app.route('/settings', methods=['GET', 'POST'])
def update_student_info():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        full_name = request.form['full_name']
        department_name = request.form['department_name']
        class_name = request.form['class_name']
        roll_number = request.form['roll_number']
        cnic = request.form['cnic']
        phone = request.form['phone']
        email = request.form['email']
        city = request.form['city']
        picture = request.files['picture']

        # Save the uploaded picture
        if picture:
            filename = secure_filename(picture.filename)
            picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            picture.save(picture_path)
            picture_url = url_for('static', filename=f'uploads/{filename}')
        else:
            picture_url = None

        # Check if the user already has a record in student_info
        cursor.execute('SELECT * FROM student_info WHERE user_id = %s', (user_id,))
        student_info = cursor.fetchone()

        if student_info:
            # Update existing record
            cursor.execute('''
                UPDATE student_info
                SET full_name = %s, department_name = %s, class_name = %s, roll_number = %s,
                    cnic = %s, phone = %s, email = %s, city = %s, picture = %s
                WHERE user_id = %s
            ''', (full_name, department_name, class_name, roll_number, cnic, phone, email, city, picture_url, user_id))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO student_info (user_id, full_name, department_name, class_name, roll_number,
                                         cnic, phone, email, city, picture)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (user_id, full_name, department_name, class_name, roll_number, cnic, phone, email, city, picture_url))

        conn.commit()
        flash('Student information updated successfully!', 'success')
        return redirect(url_for('student_info'))

    # Fetch existing student info (if any)
    cursor.execute('SELECT * FROM student_info WHERE user_id = %s', (user_id,))
    student_info = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('update_student_info.html', student_info=student_info)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
