from flask import Flask, request, send_file, session, redirect
import base64, io, os, csv
from PIL import Image
import numpy as np
from datetime import datetime
import cv2
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "facenova_pro"

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ================= HOME =================
@app.route("/")
def home():
    return """
    <style>
    body {
        margin:0;
        font-family:sans-serif;
        background: linear-gradient(135deg,#0f172a,#1e293b);
        color:white;
        text-align:center;
    }
    .card {
        margin-top:30px;
        background:rgba(255,255,255,0.05);
        padding:20px;
        border-radius:15px;
        backdrop-filter: blur(10px);
        box-shadow:0 0 20px rgba(0,0,0,0.5);
    }
    input {
        padding:10px;
        border:none;
        border-radius:10px;
        margin-bottom:10px;
    }
    button {
        padding:10px 20px;
        margin:5px;
        border:none;
        border-radius:10px;
        background:#22c55e;
        color:white;
        cursor:pointer;
    }
    button:hover {
        background:#16a34a;
    }
    video {
        border-radius:15px;
    }
    </style>

    <h1>🚀 FaceNova Ultra PRO</h1>

    <div class="card">
    <input id="name" placeholder="Enter your name"><br>

    <video id="video" width="300" autoplay></video><br><br>

    <button onclick="capture()">Scan Face</button><br><br>

    <a href="/admin"><button>Admin</button></a>
    <a href="/gallery"><button>Gallery</button></a>
    <a href="/download"><button>CSV</button></a>

    <canvas id="canvas" style="display:none;"></canvas>
    </div>

    <script>
    const video = document.getElementById('video');
    navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => video.srcObject = stream);

    function capture(){
        let name = document.getElementById("name").value;
        if(!name){ alert("Enter name"); return; }

        const canvas = document.getElementById('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        canvas.getContext('2d').drawImage(video,0,0);

        document.body.innerHTML="<h2>🔍 Scanning...</h2>";

        fetch('/login',{
            method:'POST',
            body: JSON.stringify({
                image: canvas.toDataURL('image/jpeg'),
                name: name
            }),
            headers: {"Content-Type":"application/json"}
        })
        .then(res=>res.text())
        .then(data=>document.body.innerHTML=data);
    }
    </script>
    """

# ================= LOGIN =================
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    img_data = data["image"].split(",")[1]
    name = data["name"]

    img = base64.b64decode(img_data)
    image = Image.open(io.BytesIO(img)).convert("RGB")
    np_img = np.array(image)

    gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray,1.3,5)

    if len(faces)==0:
        return "<h2>No face detected ❌</h2>"

    if not os.path.exists("photos"):
        os.mkdir("photos")

    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".jpg"
    cv2.imwrite(f"photos/{filename}", cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR))

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    if not os.path.exists("attendance.csv"):
        with open("attendance.csv","w",newline="") as f:
            csv.writer(f).writerow(["Name","Date","Time","Photo"])

    with open("attendance.csv","a",newline="") as f:
        csv.writer(f).writerow([name,date,time,filename])

    return f"<h2>✅ Welcome {name}<br>{date} {time}</h2><a href='/'>Back</a>"

# ================= ADMIN =================
@app.route("/admin")
def admin():
    rows=""
    if os.path.exists("attendance.csv"):
        with open("attendance.csv") as f:
            next(f)
            for line in f:
                d=line.strip().split(",")
                rows+=f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td></tr>"

    return f"""
    <body style="background:black;color:white;text-align:center;">
    <h1>Admin Panel</h1>
    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date</th><th>Time</th></tr>
    {rows}
    </table><br>
    <a href="/graph"><button>Graph</button></a>
    <a href="/gallery"><button>Gallery</button></a>
    <a href="/delete"><button>Delete</button></a>
    <a href="/">Home</a>
    </body>
    """

# ================= GALLERY =================
@app.route("/gallery")
def gallery():
    if not os.path.exists("photos"):
        return "No photos"

    imgs=""
    for img in os.listdir("photos"):
        imgs+=f'<img src="/photo/{img}" class="img">'

    return f"""
    <style>
    body{{background:#0f172a;color:white;text-align:center;}}
    .img{{width:120px;margin:10px;border-radius:10px;transition:0.3s;}}
    .img:hover{{transform:scale(1.2);}}
    </style>
    <h1>Gallery 📸</h1>
    {imgs}
    <br><a href="/">Back</a>
    """

@app.route("/photo/<filename>")
def photo(filename):
    return send_file(f"photos/{filename}")

# ================= GRAPH =================
@app.route("/graph")
def graph():
    if not os.path.exists("attendance.csv"):
        return "No data"

    data={}
    with open("attendance.csv") as f:
        next(f)
        for line in f:
            name=line.split(",")[0]
            data[name]=data.get(name,0)+1

    plt.figure()
    plt.bar(list(data.keys()), list(data.values()))
    plt.savefig("graph.png")

    return '<img src="/graph-img">'

@app.route("/graph-img")
def graph_img():
    return send_file("graph.png")

# ================= DELETE =================
@app.route("/delete")
def delete():
    if os.path.exists("attendance.csv"):
        os.remove("attendance.csv")
    return "<h2>Deleted</h2><a href='/admin'>Back</a>"

# ================= DOWNLOAD =================
@app.route("/download")
def download():
    return send_file("attendance.csv", as_attachment=True)

# ================= RUN =================
if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
