# ================= IMPORT =================
from flask import Flask, request, send_file
import face_recognition, base64, io
from PIL import Image
import numpy as np
import os, csv, cv2
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

# ================= ADMIN =================
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

# ================= STORAGE =================
known_faces = []
known_names = []

# ================= LOAD USER =================
def load_user(name, file):
    if os.path.exists(file):
        img = face_recognition.load_image_file(file)
        enc = face_recognition.face_encodings(img)
        if enc:
            known_faces.append(enc[0])
            known_names.append(name)

# 👉 default user (image must be in same folder)
load_user("Vasu", "vasu.jpg")

# ================= DEEPFAKE CHECK =================
def deepfake_check(img):
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    blur = cv2.Laplacian(gray, cv2.CV_64F).var()
    return blur > 50

# ================= BLINK =================
def eye_ratio(e):
    return (np.linalg.norm(e[1]-e[5]) + np.linalg.norm(e[2]-e[4])) / (2*np.linalg.norm(e[0]-e[3]))

# ================= HOME =================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <style>
    body {
        margin:0;
        background:linear-gradient(135deg,#0f172a,#1e293b);
        color:white;
        text-align:center;
        font-family:sans-serif;
    }
    video {
        width:90%;
        max-width:350px;
        border-radius:15px;
    }
    button {
        padding:12px;
        margin:8px;
        border:none;
        border-radius:10px;
        background:#22c55e;
        color:white;
        font-size:16px;
    }
    </style>
    </head>
    <body>

    <h1>🚀 FaceNova AI</h1>

    <video id="video" autoplay></video><br>

    <button onclick="startLogin()">🔐 Login</button><br>
    <button onclick="voiceLogin()">🎤 Voice</button><br>

    <a href="/register"><button>➕ Register</button></a>
    <a href="/admin-login"><button>📊 Admin</button></a>
    <a href="/download"><button>⬇️ CSV</button></a>

    <p id="status">Ready...</p>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
    const video = document.getElementById('video');

    navigator.mediaDevices.getUserMedia({video:true})
    .then(s => video.srcObject = s);

    async function startLogin(){
        document.getElementById("status").innerText = "Blink 👁️";

        let frames = [];

        for(let i=0;i<5;i++){
            await new Promise(r=>setTimeout(r,300));

            const canvas = document.getElementById('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            canvas.getContext('2d').drawImage(video,0,0);
            frames.push(canvas.toDataURL('image/jpeg'));
        }

        document.getElementById("status").innerText = "Processing...";

        fetch('/login',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({frames:frames})
        })
        .then(r=>r.text())
        .then(d=>document.body.innerHTML="<h2>"+d+"</h2>");
    }

    function voiceLogin(){
        const rec = new(window.SpeechRecognition||window.webkitSpeechRecognition)();
        rec.start();

        rec.onresult = function(e){
            const text = e.results[0][0].transcript;

            fetch('/voice',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({text:text})
            })
            .then(r=>r.text())
            .then(d=>alert(d));
        }
    }
    </script>

    </body>
    </html>
    """

# ================= REGISTER =================
@app.route("/register")
def register():
    return """
    <body style="background:black;color:white;text-align:center;">
    <h2>Register</h2>

    <input id="name" placeholder="Name"><br><br>
    <video id="video" autoplay width=300></video><br><br>
    <button onclick="cap()">Save</button>

    <canvas id="canvas" style="display:none;"></canvas>

    <script>
    const video=document.getElementById('video');
    navigator.mediaDevices.getUserMedia({video:true})
    .then(s=>video.srcObject=s);

    function cap(){
        const name=document.getElementById("name").value;

        const canvas=document.getElementById('canvas');
        canvas.width=video.videoWidth;
        canvas.height=video.videoHeight;

        canvas.getContext('2d').drawImage(video,0,0);

        fetch('/save',{
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({name:name,image:canvas.toDataURL('image/jpeg')})
        })
        .then(r=>r.text())
        .then(d=>document.body.innerHTML=d);
    }
    </script>
    </body>
    """

# ================= SAVE =================
@app.route("/save", methods=["POST"])
def save():
    data = request.json
    name = data["name"]

    img = base64.b64decode(data["image"].split(",")[1])
    image = Image.open(io.BytesIO(img)).convert("RGB")

    enc = face_recognition.face_encodings(np.array(image))
    if not enc:
        return "No face ❌"

    known_faces.append(enc[0])
    known_names.append(name)

    return f"{name} Registered ✅"

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    frames = request.json["frames"]

    blink = False
    name = None

    for f in frames:
        img = base64.b64decode(f.split(",")[1])
        image = Image.open(io.BytesIO(img)).convert("RGB")
        np_img = np.array(image)

        if not deepfake_check(np_img):
            return "Fake Detected ❌"

        enc = face_recognition.face_encodings(np_img)
        landmarks = face_recognition.face_landmarks(np_img)

        for l in landmarks:
            ear = (eye_ratio(np.array(l["left_eye"])) + eye_ratio(np.array(l["right_eye"]))) / 2
            if ear < 0.20:
                blink = True

        for e in enc:
            dist = face_recognition.face_distance(known_faces, e)
            if len(dist) > 0:
                best = np.argmin(dist)
                if dist[best] < 0.6:
                    name = known_names[best]

    if not name:
        return "Unknown ❌"
    if not blink:
        return "Blink Required ❌"

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{name}_{time}.jpg", "wb") as f:
        f.write(img)

    with open("attendance.csv", "a", newline="") as f:
        csv.writer(f).writerow([name, date, time])

    return f"Welcome {name} 🚀<br>{date} {time}"

# ================= VOICE =================
@app.route("/voice", methods=["POST"])
def voice():
    t = request.json["text"].lower()

    for n in known_names:
        if n.lower() in t:
            return f"Voice Verified {n}"

    return "Voice Fail ❌"

# ================= ADMIN =================
@app.route("/admin-login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        if request.form["user"] == ADMIN_USER and request.form["pass"] == ADMIN_PASS:
            return "<script>location='/admin'</script>"
        return "Wrong ❌"

    return """
    <form method=post>
    <input name=user placeholder="Username"><br>
    <input name=pass placeholder="Password"><br>
    <button>Login</button>
    </form>
    """

@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists("attendance.csv"):
        for line in open("attendance.csv"):
            d = line.strip().split(",")
            rows += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td></tr>"

    return f"<h1>Admin Panel</h1><table border=1>{rows}</table>"

# ================= DOWNLOAD =================
@app.route("/download")
def download():
    if os.path.exists("attendance.csv"):
        return send_file("attendance.csv", as_attachment=True)
    return "No file ❌"

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)