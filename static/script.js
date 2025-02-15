



// Access webcam for registration
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const captureBtn = document.getElementById('capture-btn');
const registerBtn = document.getElementById('register-btn');
const nameInput = document.getElementById('name');
const registerStatus = document.getElementById('register-status');

// Access webcam for attendance
const attendanceVideo = document.getElementById('attendance-video');
const attendanceCanvas = document.getElementById('attendance-canvas');
const markAttendanceBtn = document.getElementById('mark-attendance-btn');
const attendanceStatus = document.getElementById('attendance-status');

// Attendance table
const attendanceTable = document.getElementById('attendance-table').getElementsByTagName('tbody')[0];

// Start webcam for registration
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        video.srcObject = stream;
        attendanceVideo.srcObject = stream;
    })
    .catch(err => {
        console.error("Error accessing webcam: ", err);
    });


// Register face
registerBtn.addEventListener('click', async () => {
    const context = canvas.getContext('2d');
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    registerBtn.disabled = false;
    await new Promise(r => setTimeout(r, 500));
    const name = nameInput.value;
    if (!name) {
        alert("Please enter your name.");
        return;
    }

    const image = canvas.toDataURL('image/jpeg');
    const response = await fetch('http://127.0.0.1:5000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, image }),
    });

    const result = await response.json();
    registerStatus.textContent = result.message;
});

// Mark attendance
markAttendanceBtn.addEventListener('click', async () => {
    const context = attendanceCanvas.getContext('2d');
    context.drawImage(attendanceVideo, 0, 0, attendanceCanvas.width, attendanceCanvas.height);
    const image = attendanceCanvas.toDataURL('image/jpeg');

    const response = await fetch('/mark-attendance', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image }),
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
});


