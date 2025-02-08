// Load face-api.js models
Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('/models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('/models'),
]).then(startVideo);

// Start video stream
function startVideo() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => {
            video.srcObject = stream;
            attendanceVideo.srcObject = stream;
        })
        .catch(err => {
            console.error("Error accessing webcam: ", err);
        });
}

// Register face
const registerBtn = document.getElementById('register-btn');
registerBtn.addEventListener('click', async () => {
    const name = nameInput.value;
    if (!name) {
        alert("Please enter your name.");
        return;
    }

    const image = canvas.toDataURL('image/jpeg');
    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, image }),
    });

    const result = await response.json();
    registerStatus.textContent = result.message;
});

// Automatic attendance marking
const attendanceStatus = document.getElementById('attendance-status');
const attendanceTable = document.getElementById('attendance-table').getElementsByTagName('tbody')[0];

attendanceVideo.addEventListener('play', () => {
    const displaySize = { width: attendanceVideo.width, height: attendanceVideo.height };
    faceapi.matchDimensions(attendanceCanvas, displaySize);

    setInterval(async () => {
        const detections = await faceapi.detectAllFaces(attendanceVideo, new faceapi.TinyFaceDetectorOptions())
            .withFaceLandmarks()
            .withFaceDescriptors();

        if (detections.length > 0) {
            const response = await fetch('/mark-attendance', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ image: attendanceCanvas.toDataURL('image/jpeg') }),
            });

            const result = await response.json();
            attendanceStatus.textContent = result.message;

            if (result.attendance) {
                const row = attendanceTable.insertRow();
                const nameCell = row.insertCell(0);
                const dateCell = row.insertCell(1);
                const timeCell = row.insertCell(2);
                nameCell.textContent = result.attendance.name;
                dateCell.textContent = result.attendance.date;
                timeCell.textContent = result.attendance.time;
            }
        }
    }, 1000); // Check every second
});