from flask import Flask, render_template, request, redirect, url_for
import cv2
import face_recognition
import os
from datetime import datetime

app = Flask(__name__)

# Path to the directory where known face images are stored
KNOWN_FACES_DIR = 'known_faces'
# Path to the directory where attendance records will be stored
ATTENDANCE_DIR = 'attendance'

# Ensure the directories exist
os.makedirs(KNOWN_FACES_DIR, exist_ok=True)
os.makedirs(ATTENDANCE_DIR, exist_ok=True)

# Load known faces and their encodings
known_faces = []
known_names = []

for name in os.listdir(KNOWN_FACES_DIR):
    image_path = os.path.join(KNOWN_FACES_DIR, name)
    image = face_recognition.load_image_file(image_path)
    encoding = face_recognition.face_encodings(image)[0]
    known_faces.append(encoding)
    known_names.append(os.path.splitext(name)[0])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('index'))

    # Save the uploaded file temporarily
    file_path = os.path.join('static', 'temp.jpg')
    file.save(file_path)

    # Load the uploaded image
    image = face_recognition.load_image_file(file_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_faces, face_encoding)
        name = "Unknown"

        if True in matches:
            first_match_index = matches.index(True)
            name = known_names[first_match_index]

            # Mark attendance
            attendance_file = os.path.join(ATTENDANCE_DIR, f"{name}.txt")
            with open(attendance_file, 'a') as f:
                f.write(f"{datetime.now()}\n")

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)



