import os
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)

# Required to use Flask flash messages sessions
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'supersecretdevelopmentkey')

# Database configuration
db_config = {
    'host': os.environ.get('DB_HOST', '172.31.43.67'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'root@stud-reg-flask-app'),
    'database': os.environ.get('DB_DATABASE', 'studentsdb')
}

# Helper function to establish database connections cleanly
def get_db_connection():
    return mysql.connector.connect(**db_config)


# Route 1: Registration Form Handling & Validation
@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        course = request.form.get('course', '').strip()
        address = request.form.get('address', '').strip()
        contact = request.form.get('contact', '').strip()

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

            flash('Student Registered Successfully!', 'success')
            return redirect(url_for('register'))

        except mysql.connector.Error as err:
            flash(f'Database Error: {err.msg}', 'danger')
            return redirect(url_for('register'))

    return render_template('register.html')


# Route 2: Data Retrieval Route
@app.route('/students', methods=['GET'])
def students():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM students")
        students_list = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return render_template('students.html', students=students_list)
        
    except mysql.connector.Error as err:
        return f"Failed to retrieve data from database: {err.msg}", 500


# Route 3: Edit Student (GET to show form, POST to update)
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
            return redirect(url_for('students')) # Fixed endpoint name from show_students to students

        # GET Request execution
        cursor.execute("SELECT * FROM students WHERE id = %s", (id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return render_template('edit.html', student=student)

    except mysql.connector.Error as err:
        flash(f'Error: {err.msg}', 'danger')
        return redirect(url_for('students')) # Fixed endpoint name from show_students to students


# Route 4: Delete Student
@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM students WHERE id = %s", (id,))
        conn.commit()
        
        cursor.close()
        conn.close()
        flash('Student record deleted successfully!', 'warning')
    except mysql.connector.Error as err:
        flash(f'Error deleting record: {err.msg}', 'danger')
        
    return redirect(url_for('students')) # Fixed endpoint name from show_students to students


# Keep execution at the absolute bottom of the script
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)