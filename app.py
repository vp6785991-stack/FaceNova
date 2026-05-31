from flask import Flask, request, send_file
import os
import csv
import base64
from datetime import datetime
import cv2
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

app = Flask(__name__)

# -------------------- FOLDERS --------------------

DATA_DIR = "data"
GRAPH_DIR = "graphs"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

ATT_FILE = os.path.join(DATA_DIR, "attendance.csv")

# -------------------- FACE DETECTOR --------------------

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

# -------------------- STYLE --------------------

STYLE = """
<style>

body{
    margin:0;
    font-family:Arial;
    background:linear-gradient(135deg,#0f172a,#1e3a8a,#312e81);
    color:white;
    min-height:100vh;
}

.container{
    width:90%;
    max-width:1000px;
    margin:auto;
    margin-top:20px;
    background:rgba(255,255,255,0.08);
    padding:25px;
    border-radius:25px;
    backdrop-filter:blur(12px);
    box-shadow:0 0 25px rgba(0,0,0,0.4);
}

h1,h2,h3{
    text-align:center;
}

button{
    padding:12px 22px;
    border:none;
    border-radius:15px;
    background:linear-gradient(45deg,#2563eb,#7c3aed);
    color:white;
    cursor:pointer;
    margin:8px;
    font-size:15px;
    transition:0.3s;
}

button:hover{
    transform:scale(1.05);
    opacity:0.9;
}

input{
    padding:12px;
    border:none;
    border-radius:12px;
    width:90%;
    margin:8px;
}

.card-grid{
    display:grid;
    grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
    gap:20px;
    margin-top:25px;
}

.card{
    background:rgba(255,255,255,0.08);
    padding:20px;
    border-radius:20px;
    text-align:center;
}

img{
    border-radius:15px;
    margin:10px;
}

video{
    border-radius:20px;
    border:3px solid white;
}

table{
    width:100%;
    border-collapse:collapse;
    margin-top:20px;
}

th,td{
    border:1px solid rgba(255,255,255,0.2);
    padding:12px;
    text-align:center;
}

th{
    background:#1e40af;
}

.present{
    background:green;
}

.absent{
    background:red;
}

.calendar{
    display:grid;
    grid-template-columns:repeat(7,1fr);
    gap:10px;
    margin-top:20px;
}

.day{
    padding:15px;
    border-radius:12px;
    text-align:center;
    font-weight:bold;
}

.green{
    background:green;
}

.red{
    background:red;
}

.gray{
    background:gray;
}

</style>
"""

# -------------------- HOME --------------------

@app.route("/")
def home():

    total_students = len([
        x for x in os.listdir(DATA_DIR)
        if os.path.isdir(os.path.join(DATA_DIR, x))
    ])

    total_attendance = 0

    if os.path.exists(ATT_FILE):
        with open(ATT_FILE) as f:
            total_attendance = len(list(csv.reader(f)))

    return f"""
    {STYLE}

    <div class='container'>

    <h1>🚀 FaceNova AI</h1>

    <h3>Smart AI Attendance & Authentication System</h3>

    <div class='card-grid'>

        <div class='card'>
            <h2>{total_students}</h2>
            <p>Registered Students</p>
        </div>

        <div class='card'>
            <h2>{total_attendance}</h2>
            <p>Total Attendance</p>
        </div>

        <div class='card'>
            <h2>AI</h2>
            <p>Live Face Scan</p>
        </div>

    </div>

    <hr>

    <h2>📸 Upload Student Faces</h2>

    <form action='/upload' method='POST' enctype='multipart/form-data'>

    <input type='text' name='name' placeholder='Student Name' required>

    <br>

    <input type='file' name='photos' multiple required>

    <br>

    <button type='submit'>Upload Faces</button>

    </form>

    <hr>

    <h2>🎥 Live Camera Scan</h2>

    <video id='cam' width='320' autoplay playsinline></video>

    <br><br>

    <button onclick='snap()'>📷 Scan Face</button>

    <canvas id='canvas' style='display:none;'></canvas>

    <form id='camForm' action='/camera' method='POST'>

        <input type='hidden' name='img' id='imgdata'>

    </form>

    <hr>

    <div style='text-align:center;'>

    <a href='/gallery'><button>🖼 Gallery</button></a>

    <a href='/graph'><button>📊 Graph</button></a>

    <a href='/calendar'><button>📅 Calendar</button></a>

    <a href='/admin'><button>⚙ Admin</button></a>

    </div>

    </div>

<script>

navigator.mediaDevices.getUserMedia({{
    video:true
}})
.then(stream=>{{
    document.getElementById('cam').srcObject = stream;
}})
.catch(err=>{{
    alert("Camera access failed");
}});

function snap(){{

    let video = document.getElementById("cam");

    let canvas = document.getElementById("canvas");

    canvas.width = video.videoWidth;

    canvas.height = video.videoHeight;

    let ctx = canvas.getContext("2d");

    ctx.drawImage(video,0,0);

    let data = canvas.toDataURL("image/jpeg",0.8);

    document.getElementById("imgdata").value = data;

    document.getElementById("camForm").submit();

}}

</script>
"""

# -------------------- UPLOAD --------------------

@app.route("/upload", methods=["POST"])
def upload():

    try:

        name = request.form["name"]

        files = request.files.getlist("photos")

        user_dir = os.path.join(DATA_DIR, name)

        os.makedirs(user_dir, exist_ok=True)

        for f in files:

            filename = f"{datetime.now().timestamp()}.jpg"

            save_path = os.path.join(user_dir, filename)

            f.save(save_path)

        return f"""
        {STYLE}

        <div class='container'>

        <h2>✅ Faces Uploaded Successfully</h2>

        <a href='/'><button>🏠 Home</button></a>

        </div>
        """

    except Exception as e:

        return f"""
        {STYLE}

        <div class='container'>

        <h2>Upload Error</h2>

        <p>{str(e)}</p>

        </div>
        """

# -------------------- FACE DETECTION --------------------

def detect_face(image_path):

    img = cv2.imread(image_path)

    if img is None:
        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5
    )

    return len(faces) > 0

# -------------------- CAMERA --------------------

@app.route("/camera", methods=["POST"])
def camera():

    try:

        data = request.form.get("img")

        if not data:
            return "No image received"

        header, encoded = data.split(",", 1)

        img_bytes = base64.b64decode(encoded)

        filename = f"camera_{datetime.now().timestamp()}.jpg"

        full_path = os.path.join(DATA_DIR, filename)

        with open(full_path, "wb") as f:
            f.write(img_bytes)

        has_face = detect_face(full_path)

        if has_face:
            person = "Face Detected"
            status = "Present"
        else:
            person = "Unknown"
            status = "Absent"

        today = datetime.now().strftime("%Y-%m-%d")

        with open(ATT_FILE, "a", newline="") as f:

            writer = csv.writer(f)

            writer.writerow([person, today, status])

        return f"""
        {STYLE}

        <div class='container'>

        <h2>✅ Scan Complete</h2>

        <h3>{person}</h3>

        <p>Status: {status}</p>

        <img src='/cam/{filename}' width='260'>

        <br><br>

        <a href='/'><button>🏠 Home</button></a>

        </div>
        """

    except Exception as e:

        return f"""
        {STYLE}

        <div class='container'>

        <h2>Camera Error</h2>

        <p>{str(e)}</p>

        </div>
        """

# -------------------- CAMERA IMAGE --------------------

@app.route("/cam/<file>")
def cam(file):

    return send_file(os.path.join(DATA_DIR, file))

# -------------------- GALLERY --------------------

@app.route("/gallery")
def gallery():

    gallery_html = ""

    for user in os.listdir(DATA_DIR):

        user_dir = os.path.join(DATA_DIR, user)

        if not os.path.isdir(user_dir):
            continue

        for img in os.listdir(user_dir):

            gallery_html += f"""

            <div class='card'>

            <h3>{user}</h3>

            <img src='/img/{user}/{img}' width='220'>

            </div>
            """

    return f"""
    {STYLE}

    <div class='container'>

    <h1>🖼 Face Gallery</h1>

    <div class='card-grid'>

    {gallery_html}

    </div>

    <br>

    <a href='/'><button>🏠 Home</button></a>

    </div>
    """

# -------------------- IMAGE ROUTE --------------------

@app.route("/img/<user>/<file>")
def img(user, file):

    return send_file(os.path.join(DATA_DIR, user, file))

# -------------------- GRAPH --------------------

@app.route("/graph")
def graph():

    try:

        attendance = {}

        if os.path.exists(ATT_FILE):

            with open(ATT_FILE) as f:

                reader = csv.reader(f)

                for row in reader:

                    if len(row) >= 3:

                        attendance[row[0]] = attendance.get(row[0], 0) + 1

        if len(attendance) == 0:

            return f"""
            {STYLE}
            <div class='container'>
            <h2>No attendance data found</h2>
            <a href='/'>Home</a>
            </div>
            """

        plt.figure(figsize=(7,5))

        plt.bar(
            list(attendance.keys()),
            list(attendance.values())
        )

        plt.xlabel("Users")
        plt.ylabel("Attendance")
        plt.title("FaceNova Analytics")

        graph_path = os.path.join(GRAPH_DIR, "graph.png")

        plt.savefig(graph_path)

        plt.close()

        return f"""
        {STYLE}
        <div class='container'>
        <h1>📊 Attendance Graph</h1>
        <img src='/graph-image' width='100%'>
        <br><br>
        <a href='/'><button>🏠 Home</button></a>
        </div>
        """

    except Exception as e:

        return f"""
        <h2>Graph Error</h2>
        <pre>{str(e)}</pre>
        """

# -------------------- CALENDAR --------------------

@app.route("/calendar")
def calendar():

    records = {}

    if os.path.exists(ATT_FILE):

        with open(ATT_FILE) as f:

            reader = csv.reader(f)

            for row in reader:

                if len(row) >= 3:

                    name = row[0]
                    date = row[1]
                    status = row[2]

                    records[date] = status

    calendar_html = ""

    for date, status in records.items():

        color = "green" if status == "Present" else "red"

        calendar_html += f"""

        <div class='day {color}'>

        <p>{date}</p>

        <b>{status}</b>

        </div>
        """

    return f"""
    {STYLE}

    <div class='container'>

    <h1>📅 Attendance Calendar</h1>

    <div class='calendar'>

    {calendar_html}

    </div>

    <br>

    <a href='/'><button>🏠 Home</button></a>

    </div>
    """

# -------------------- ADMIN --------------------

@app.route("/admin")
def admin():

    table_rows = ""

    if os.path.exists(ATT_FILE):

        with open(ATT_FILE) as f:

            reader = csv.reader(f)

            for row in reader:

                if len(row) >= 3:

                    table_rows += f"""

                    <tr>

                    <td>{row[0]}</td>

                    <td>{row[1]}</td>

                    <td>{row[2]}</td>

                    </tr>
                    """

    return f"""
    {STYLE}

    <div class='container'>

    <h1>⚙ Admin Dashboard</h1>

    <table>

    <tr>

    <th>Name</th>

    <th>Date</th>

    <th>Status</th>

    </tr>

    {table_rows}

    </table>

    <br>

    <a href='/download'><button>⬇ Download CSV</button></a>

    <a href='/delete'><button>🗑 Delete Data</button></a>

    <a href='/'><button>🏠 Home</button></a>

    </div>
    """

# -------------------- DOWNLOAD --------------------

@app.route("/download")
def download():

    if os.path.exists(ATT_FILE):

        return send_file(ATT_FILE, as_attachment=True)

    return "No CSV file found"

# -------------------- DELETE --------------------

@app.route("/delete")
def delete():

    try:

        if os.path.exists(ATT_FILE):
            os.remove(ATT_FILE)

        for root, dirs, files in os.walk(DATA_DIR):

            for file in files:

                if file.endswith(".jpg") or file.endswith(".png"):

                    try:
                        os.remove(os.path.join(root, file))
                    except:
                        pass

        return f"""
        {STYLE}

        <div class='container'>

        <h2>🗑 Data Deleted Successfully</h2>

        <a href='/admin'><button>Back</button></a>

        </div>
        """

    except Exception as e:

        return f"""
        {STYLE}

        <div class='container'>

        <h2>Delete Error</h2>

        <p>{str(e)}</p>

        </div>
        """

# -------------------- RUN --------------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000)
