from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'

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
    if 'username' in session:
        user = session['username']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Fetch buses
            cursor.execute('SELECT * FROM buses')
            buses = cursor.fetchall()  # Fetch all rows from the first query

            # Fetch notifications
            cursor.execute('SELECT * FROM notifications ORDER BY created_at DESC')
            notifications = cursor.fetchall()  # Fetch all rows from the second query
            print(notifications)  # Debugging: Print notifications to console

            return render_template('dashboard.html', user=user, buses=buses, notifications=notifications)
        finally:
            cursor.close()
            conn.close()
    return redirect(url_for('login'))

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
            user = cursor.fetchone()
            if user:
                session['username'] = user['username']
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
@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('admin.html')

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

# Add Schedule Route
@app.route('/admin/add_schedule', methods=['GET', 'POST'])
def add_schedule():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        time_fg_to_bjc = request.form['time_fg_to_bjc']
        route_fg_to_bjc = request.form['route_fg_to_bjc']
        time_bjc_to_fg = request.form['time_bjc_to_fg']
        route_bjc_to_fg = request.form['route_bjc_to_fg']
        time_fg_to_kh_fc = request.form['time_fg_to_kh_fc']
        route_fg_to_kh_fc = request.form['route_fg_to_kh_fc']
        time_kh_fc_to_ac = request.form['time_kh_fc_to_ac']
        route_kh_fc_to_ac = request.form['route_kh_fc_to_ac']
        day_type = request.form['day_type']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO schedules (
                    time_fg_to_bjc, route_fg_to_bjc, time_bjc_to_fg, route_bjc_to_fg,
                    time_fg_to_kh_fc, route_fg_to_kh_fc, time_kh_fc_to_ac, route_kh_fc_to_ac, day_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                time_fg_to_bjc, route_fg_to_bjc, time_bjc_to_fg, route_bjc_to_fg,
                time_fg_to_kh_fc, route_fg_to_kh_fc, time_kh_fc_to_ac, route_kh_fc_to_ac, day_type
            ))
            conn.commit()
            flash('Schedule added successfully!', 'success')
            return redirect(url_for('admin'))
        finally:
            cursor.close()
            conn.close()
    return render_template('add_schedule.html')

# Serve Analytics Section
@app.route('/admin/analytics')
def analytics():
    return render_template('analytics.html')

# Serve Buses Section
@app.route('/admin/buses')
def buses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM buses')
        buses = cursor.fetchall()
        return render_template('buses.html', buses=buses)
    finally:
        cursor.close()
        conn.close()

# Serve Routes Section
@app.route('/admin/routes')
def routes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM routes')
        routes = cursor.fetchall()
        return render_template('routes.html', routes=routes)
    finally:
        cursor.close()
        conn.close()

# Serve Users Section
@app.route('/admin/users')
def users():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        return render_template('users.html', users=users)
    finally:
        cursor.close()
        conn.close()

# Send Notification Route
@app.route('/send_notification', methods=['POST'])
def send_notification():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    try:
        # Get form data
        title = request.form['title']
        message = request.form['message']
        notification_type = request.form['type']

        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO notifications (title, message, type) VALUES (%s, %s, %s)',
                (title, message, notification_type)
            )
            conn.commit()
            return jsonify({'success': True, 'message': 'Notification sent successfully!'})
        finally:
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error: {e}")  # Log the error
        return jsonify({'success': False, 'message': 'Failed to send notification. Please try again.'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)