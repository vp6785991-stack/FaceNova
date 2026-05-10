from flask import Flask, request, send_file
import os
import csv
import base64
from datetime import datetime

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import cv2

app = Flask(__name__)

# -------------------- FOLDERS --------------------

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

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
    text-align:center;
    color:white;
    background: linear-gradient(135deg,#020617,#0f172a,#1e3a8a,#9333ea);
}

.container{
    width:90%;
    max-width:750px;
    margin:auto;
    margin-top:20px;
    padding:20px;
    background:rgba(0,0,0,0.55);
    border-radius:20px;
}

button{
    padding:10px 20px;
    border:none;
    border-radius:10px;
    background:#22c55e;
    color:white;
    cursor:pointer;
    margin:5px;
}

button:hover{
    opacity:0.9;
}

input{
    padding:10px;
    border-radius:10px;
    border:none;
}

table{
    margin:auto;
    background:white;
    color:black;
}

img{
    border-radius:10px;
    margin:10px;
}

video{
    border-radius:15px;
    border:3px solid white;
}

h1{
    color:#60a5fa;
}

</style>
"""

# -------------------- HOME --------------------

@app.route("/")
def home():

    return f"""
    {STYLE}

    <h1>🚀 FaceNova Ultra AI</h1>

    <div class='container'>

    <h2>📸 Upload Student Faces</h2>

    <form action='/upload' method='post' enctype='multipart/form-data'>

        <input type='text' name='name' placeholder='Enter Student Name' required>

        <br><br>

        <input type='file' name='photos' multiple required>

        <br><br>

        <button type='submit'>Save Faces</button>

    </form>

    <hr>

    <h2>🎥 Live Camera Scan</h2>

    <video id='cam' width='320' autoplay playsinline></video>

    <br><br>

    <button onclick='snap()'>📷 Scan Face</button>

    <canvas id='canvas' style='display:none;'></canvas>

    <form id='camForm' action='/camera' method='post'>

        <input type='hidden' name='img' id='imgdata'>

    </form>

    <br>

    <a href='/gallery'><button>🖼 Gallery</button></a>

    <a href='/graph'><button>📊 Graph</button></a>

    <a href='/admin'><button>⚙️ Admin</button></a>

    </div>

<script>

navigator.mediaDevices.getUserMedia({
    video:true
})
.then(stream=>{
    document.getElementById('cam').srcObject = stream;
})
.catch(err=>{
    alert("Camera access failed");
});

function snap(){

    let canvas = document.getElementById("canvas");
    let video = document.getElementById("cam");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    let ctx = canvas.getContext("2d");

    ctx.drawImage(video,0,0);

    let data = canvas.toDataURL("image/jpeg",0.8);

    document.getElementById("imgdata").value = data;

    document.getElementById("camForm").submit();
}

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

        <h2>✅ Faces Saved Successfully</h2>

        <a href='/'><button>Back</button></a>

        </div>
        """

    except Exception as e:

        return f"""
        {STYLE}

        <div class='container'>

        <h2>Upload Error</h2>

        <p>{str(e)}</p>

        <a href='/'><button>Back</button></a>

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

        header, encoded = data.split(",",1)

        img_bytes = base64.b64decode(encoded)

        filename = f"cam_{datetime.now().timestamp()}.jpg"

        full_path = os.path.join(DATA_DIR, filename)

        with open(full_path, "wb") as f:
            f.write(img_bytes)

        has_face = detect_face(full_path)

        if has_face:
            person = "Face Detected"
            status = "Present"
        else:
            person = "Unknown"
            status = "No Face"

        today = datetime.now().strftime("%Y-%m-%d")

        already_marked = False

        if os.path.exists(ATT_FILE):

            with open(ATT_FILE) as f:

                rows = list(csv.reader(f))

                for row in rows:

                    if len(row) >= 3:

                        if row[0] == person and row[1] == today:

                            already_marked = True

        if not already_marked:

            with open(ATT_FILE, "a", newline="") as f:

                writer = csv.writer(f)

                writer.writerow([person, today, status])

        return f"""
        {STYLE}

        <div class='container'>

        <h2>✅ Scan Complete</h2>

        <h3>{person}</h3>

        <p>Status: {status}</p>

        <img src='/cam/{filename}' width='250'>

        <br><br>

        <a href='/'><button>Back</button></a>

        </div>
        """

    except Exception as e:

        return f"""
        {STYLE}

        <div class='container'>

        <h2>Camera Error</h2>

        <p>{str(e)}</p>

        <a href='/'><button>Back</button></a>

        </div>
        """

# -------------------- SHOW CAMERA IMAGE --------------------

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

            <div>

            <h3>{user}</h3>

            <img src='/img/{user}/{img}' width='150'>

            </div>

            """

    return f"""
    {STYLE}

    <h1>🖼 Face Gallery</h1>

    {gallery_html}

    <br>

    <a href='/'><button>🏠 Home</button></a>
    """

@app.route("/img/<user>/<file>")
def img(user, file):

    return send_file(os.path.join(DATA_DIR, user, file))

# -------------------- GRAPH --------------------

@app.route("/graph")
def graph():

    attendance = {}

    if os.path.exists(ATT_FILE):

        with open(ATT_FILE) as f:

            reader = csv.reader(f)

            for row in reader:

                if len(row) >= 3:

                    attendance[row[0]] = attendance.get(row[0], 0) + 1

    plt.figure(figsize=(7,5))

    plt.bar(attendance.keys(), attendance.values())

    plt.xlabel("Users")

    plt.ylabel("Scans")

    plt.title("Attendance Graph")

    graph_path = os.path.join(DATA_DIR, "graph.png")

    plt.savefig(graph_path)

    plt.close()

    return f"""
    {STYLE}

    <h1>📊 Attendance Graph</h1>

    <img src='/graph-image' width='500'>

    <br>

    <a href='/'><button>🏠 Home</button></a>
    """

@app.route("/graph-image")
def graph_image():

    return send_file(os.path.join(DATA_DIR, "graph.png"))

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

    <h1>⚙️ Admin Panel</h1>

    <table border='1' cellpadding='10'>

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

        <a href='/admin'><button>Back</button></a>

        </div>
        """

# -------------------- RUN --------------------

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=10000)
