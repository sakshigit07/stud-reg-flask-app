import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

# Required to use Flask flash messages sessions
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretdevelopmentkey')

# Database configuration
# Using os.environ.get allows you to transition seamlessly from local testing to EC2/Docker deployment
db_config = {
    'host': os.environ.get('DB_HOST', 'db'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'root@stud-reg-flask-app'),
    'database': os.environ.get('DB_DATABASE', 'studentsdb')
}

# Helper function to establish database connections cleanly
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Requirement 1 & 2: Registration Form Handling & Validation
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Using .get() prevents KeyError if a field is completely missing
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        address = request.form.get('address', '').strip()
        contact = request.form.get('contact', '').strip()

        # Server-side validation check (Ensuring mandatory fields are filled out)
        if not name or not email or not phone:
            flash('Name, Email, and Phone Number are required fields.', 'danger')
            return redirect(url_for('register'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = '''
            INSERT INTO students (name, email, phone, course, address, contact)
            VALUES (%s, %s, %s, %s, %s, %s)
            '''
            values = (name, email, phone, course, address, contact)

            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()

            # Elegant UI feedback using flash instead of raw string text
            flash('Student Registered Successfully!', 'success')
            return redirect(url_for('register'))

        except mysql.connector.Error as err:
            flash(f'Database Error: {err.msg}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


# Requirement 3: Data Retrieval Route
@app.route('/students', methods=['GET'])
def show_students():
    try:
        conn = get_db_connection()
        # dictionary=True maps column names to keys, which makes looping in Jinja HTML extremely clean
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM students")
        students_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        # Pass the retrieved data list to the view template
        return render_template('students.html', students=students_list)
        
    except mysql.connector.Error as err:
        return f"Failed to retrieve data from database: {err.msg}", 500


if __name__ == '__main__':
    # Configured for external access on port 5000
    app.run(host='0.0.0.0', port=5000, debug=True)

# Route: Edit Student (GET to show the edit form with filled data, POST to update it)
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            course = request.form.get('course', '').strip()
            address = request.form.get('address', '').strip()
            contact = request.form.get('contact', '').strip()

            # Update database query
            query = '''
            UPDATE students 
            SET name=%s, email=%s, phone=%s, course=%s, address=%s, contact=%s 
            WHERE id=%s
            '''
            cursor.execute(query, (name, email, phone, course, address, contact, id))
            conn.commit()
            
            cursor.close()
            conn.close()
            flash('Student profile updated successfully!', 'success')
            return redirect(url_for('show_students'))

        # GET Request: Fetch existing data to populate the edit form
        cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return render_template('edit.html', student=student)

    except mysql.connector.Error as err:
        flash(f'Error: {err.msg}', 'danger')
        return redirect(url_for('show_students'))


# Route: Delete Student
@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete row matching the unique ID
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        flash('Student record deleted successfully!', 'warning')
    except mysql.connector.Error as err:
        flash(f'Error deleting record: {err.msg}', 'danger')
        
    return redirect(url_for('show_students'))