from flask import Flask, request, send_file
import base64
from PIL import Image
import io
import numpy as np
import os
import csv
from datetime import datetime
import cv2

app = Flask(__name__)

# Face detector (lightweight)
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ================= HOME =================
@app.route("/")
def home():
    return """
    <html>
    <body style="background:#0f172a;color:white;text-align:center;font-family:Arial;">
        <h1>🚀 FaceNova Lite</h1>

        <video id="video" width="300" autoplay></video><br><br>

        <button onclick="capture()">Login</button>

        <br><br>
        <a href="/admin"><button>Admin Panel</button></a>
        <a href="/download"><button>Download CSV</button></a>

        <canvas id="canvas" style="display:none;"></canvas>

        <script>
        const video = document.getElementById('video');

        navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream);

        function capture() {
            const canvas = document.getElementById('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);

            const data = canvas.toDataURL('image/jpeg');

            fetch('/login', {
                method: 'POST',
                body: data
            })
            .then(res => res.text())
            .then(data => document.body.innerHTML = data);
        }
        </script>
    </body>
    </html>
    """

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.data.decode("utf-8").split(",")[1]
        image_bytes = base64.b64decode(data)

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_np = np.array(image)

        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return "<h2>No face detected ❌</h2>"

        # Fake login success (for now)
        name = "User"

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        if not os.path.exists("attendance.csv"):
            with open("attendance.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Name", "Date", "Time"])

        already = False
        with open("attendance.csv", "r") as f:
            for line in f:
                if name in line and date in line:
                    already = True
                    break

        if not already:
            with open("attendance.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([name, date, time])

        return f"<h2>Welcome {name} 🚀<br>{date} {time}</h2>"

    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"

# ================= ADMIN =================
@app.route("/admin")
def admin():
    if not os.path.exists("attendance.csv"):
        return "<h2>No data ❌</h2>"

    rows = ""
    with open("attendance.csv", "r") as f:
        next(f)
        for line in f:
            name, date, time = line.strip().split(",")
            rows += f"<tr><td>{name}</td><td>{date}</td><td>{time}</td></tr>"

    return f"""
    <html>
    <body style="background:#0f172a;color:white;text-align:center;">
    <h1>Admin Panel</h1>
    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date</th><th>Time</th></tr>
    {rows}
    </table>
    <br>
    <a href="/delete"><button>Delete All</button></a>
    <a href="/"><button>Back</button></a>
    </body>
    </html>
    """

# ================= DELETE =================
@app.route("/delete")
def delete():
    if os.path.exists("attendance.csv"):
        os.remove("attendance.csv")
    return "<h2>All data deleted ✅</h2><a href='/'>Back</a>"

# ================= DOWNLOAD =================
@app.route("/download")
def download():
    if os.path.exists("attendance.csv"):
        return send_file("attendance.csv", as_attachment=True)
    return "<h2>No file ❌</h2>"

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
