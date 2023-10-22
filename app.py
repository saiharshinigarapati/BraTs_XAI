from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import os
import sqlite3
from werkzeug.utils import secure_filename
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'bdd288b366f6cc19eaf0a5c2b847e6c0'

# SQLite Database
db = sqlite3.connect('users.db', check_same_thread=False)
cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS signup (
        email TEXT PRIMARY KEY,
        full_name TEXT,
        password TEXT,
        date_of_birth DATE,
        gender TEXT
    )
''')
# Create the 'images' table with the 'image_data' column
cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT,
        dob TEXT,
        image_data BLOB
    )
''')
db.commit()
db.close()
import os

# Directory path where the uploads folder should be located
uploads_dir = os.path.join(os.getcwd(), 'uploads')

# Create the uploads folder if it doesn't exist
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)

@app.route('/')
def home():
    return render_template('base.html')

@app.route('/signup.html', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        full_name = request.form['full_name']
        password = request.form['password']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']

        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO signup (email, full_name, password, date_of_birth, gender)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, full_name, password, date_of_birth, gender))
        db.commit()
        db.close()

        flash('Account created successfully!', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login.html', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM signup WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session['email'] = user[0]
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Please check your credentials.', 'danger')

    return render_template('login.html')
# ...

@app.route('/account/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'email' in session:
        email = session['email']

        # Fetch user data from the database
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute('SELECT * FROM signup WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            full_name = user[1]  # Retrieve full_name from the user's data

            if request.method == 'POST':
                # Handle image upload
                image = request.files['image']

                # Ensure the user selected a file
                if image.filename != '':
                    # Read the binary data of the uploaded image
                    image_data = image.read()

                    # Store image data in the database
                    cursor.execute('''
                        INSERT INTO user_data (full_name, email, dob, image_data)
                        VALUES (?, ?, ?, ?)
                    ''', (full_name, email, user[3], sqlite3.Binary(image_data)))
                    db.commit()

                    flash('Image uploaded successfully!', 'success')

                    # Redirect to a page that displays the uploaded image
                    return redirect(url_for('display_image'))

            db.close()
            return render_template('dashboard.html', full_name=full_name, email=email, date_of_birth=user[3])
        else:
            flash('User not found.', 'danger')
            db.close()
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# ...



from flask import Response

# ...

@app.route('/account/display_image')
def display_image():
    if 'email' in session:
        db = sqlite3.connect('users.db')
        cursor = db.cursor()
        cursor.execute('SELECT image_data FROM user_data WHERE email = ?', (session['email'],))
        image_data = cursor.fetchone()
        db.close()

        if image_data:
            return Response(image_data[0], content_type='image/jpeg')  # Adjust content type as needed
        else:
            return "Image not found."
    else:
        return redirect(url_for('login'))





@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
