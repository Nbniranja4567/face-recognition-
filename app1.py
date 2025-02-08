
from flask import Flask, request, jsonify, render_template
import face_recognition
import numpy as np
import sqlite3
import os
from datetime import datetime
from PIL import Image
from io import BytesIO

app = Flask(__name__)

# Database setup
DATABASE = 'attendance.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS faces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                encoding TEXT NOT NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL
            )
        ''')
        conn.commit()

init_db()

# Helper function to save face encoding to the database
def save_face_encoding(name, encoding):
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO faces (name, encoding) VALUES (?, ?)', (name, encoding.tobytes()))
        conn.commit()

# Helper function to load all face encodings from the database
def load_face_encodings():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT name, encoding FROM faces')
        return [(row[0], np.frombuffer(row[1], dtype=np.float64)) for row in cursor.fetchall()]

# Helper function to save attendance record
def save_attendance(name):
    now = datetime.now()
    date = now.strftime('%Y-%m-%d')
    time = now.strftime('%H:%M:%S')
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('INSERT INTO attendance (name, date, time) VALUES (?, ?, ?)', (name, date, time))
        conn.commit()

# Register face endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    image_data = data.get('image')

    if not name or not image_data:
        return jsonify({'message': 'Name and image are required'}), 400

    # Decode image from base64
    import base64
    image_bytes = base64.b64decode(image_data.split(',')[1])
    image = Image.open(BytesIO(image_bytes))

    # Ensure the image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    # Convert the image to a numpy array
    image_array = np.array(image)
    face_encodings = face_recognition.face_encodings(image_array)

    if not face_encodings:
        return jsonify({'message': 'No face detected'}), 400

    face_encoding = face_encodings[0]
    save_face_encoding(name, face_encoding)
    os.remove('temp.jpg')

    return jsonify({'message': 'Face registered successfully'}), 200

# Mark attendance endpoint
@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({'message': 'Image is required'}), 400

    # Decode image from base64
    import base64
    image_bytes = base64.b64decode(image_data.split(',')[1])
    with open('temp.jpg', 'wb') as f:
        f.write(image_bytes)

    # Load image and compute face encoding
    image = face_recognition.load_image_file('temp.jpg')
    face_encodings = face_recognition.face_encodings(image)

    if not face_encodings:
        return jsonify({'message': 'No face detected'}), 400

    face_encoding = face_encodings[0]
    os.remove('temp.jpg')

    # Compare with registered faces
    registered_faces = load_face_encodings()
    for name, registered_encoding in registered_faces:
        match = face_recognition.compare_faces([registered_encoding], face_encoding, tolerance=0.5)
        if match[0]:
            save_attendance(name)
            return jsonify({
                'message': 'Attendance marked successfully',
                'attendance': {
                    'name': name,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': datetime.now().strftime('%H:%M:%S')
                }
            }), 200

    return jsonify({'message': 'Face not recognized'}), 400

# Get attendance records endpoint
@app.route('/attendance', methods=['GET'])
def get_attendance():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.execute('SELECT name, date, time FROM attendance ORDER BY date DESC, time DESC')
        records = cursor.fetchall()
        return jsonify([{'name': row[0], 'date': row[1], 'time': row[2]} for row in records]), 200

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)



