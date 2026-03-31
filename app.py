from flask import Flask, request, send_file, session, redirect
import base64, io, os, csv
from PIL import Image
import numpy as np
from datetime import datetime
import cv2
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "facenova_secret"

# ================= FACE DETECTION =================
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# ================= HOME =================
@app.route("/")
def home():
    return """
    <html>
    <body style="background:#0f172a;color:white;text-align:center;">
        <h1>🚀 FaceNova Pro</h1>

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

            fetch('/login', { method: 'POST', body: data })
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
        img_np = np.array(image)

        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        if len(faces) == 0:
            return "<h2>No face detected ❌</h2>"

        name = "User"

        now = datetime.now()
        date = now.strftime("%Y-%m-%d")
        time = now.strftime("%H:%M:%S")

        if not os.path.exists("attendance.csv"):
            with open("attendance.csv", "w", newline="") as f:
                csv.writer(f).writerow(["Name", "Date", "Time"])

        already = False
        with open("attendance.csv", "r") as f:
            for line in f:
                if name in line and date in line:
                    already = True

        if not already:
            with open("attendance.csv", "a", newline="") as f:
                csv.writer(f).writerow([name, date, time])

        return f"<h2>Welcome {name} 🚀<br>{date} {time}</h2>"

    except Exception as e:
        return f"<h2>Error: {str(e)}</h2>"

# ================= ADMIN LOGIN =================
@app.route("/admin-login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        if request.form["user"] == "admin" and request.form["pass"] == "1234":
            session["admin"] = True
            return redirect("/admin")
        return "Wrong ❌"

    return """
    <body style="background:black;color:white;text-align:center;">
    <h2>Admin Login</h2>
    <form method="post">
    <input name="user" placeholder="Username"><br><br>
    <input name="pass" type="password" placeholder="Password"><br><br>
    <button>Login</button>
    </form>
    </body>
    """

# ================= ADMIN PANEL =================
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin-login")

    rows = ""
    if os.path.exists("attendance.csv"):
        with open("attendance.csv") as f:
            next(f)
            for line in f:
                d = line.strip().split(",")
                rows += f"<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td></tr>"

    return f"""
    <body style="background:#0f172a;color:white;text-align:center;">
    <h1>Admin Panel</h1>

    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date</th><th>Time</th></tr>
    {rows}
    </table>

    <br>
    <a href="/graph"><button>Show Graph</button></a>
    <a href="/delete"><button>Delete All</button></a>
    <a href="/logout"><button>Logout</button></a>
    </body>
    """

# ================= GRAPH =================
@app.route("/graph")
def graph():
    if not os.path.exists("attendance.csv"):
        return "No data"

    data = {}
    with open("attendance.csv") as f:
        next(f)
        for line in f:
            name = line.split(",")[0]
            data[name] = data.get(name, 0) + 1

    names = list(data.keys())
    counts = list(data.values())

    plt.figure()
    plt.bar(names, counts)
    plt.savefig("graph.png")

    return '<img src="/graph-img">'

@app.route("/graph-img")
def graph_img():
    return send_file("graph.png", mimetype='image/png')

# ================= DELETE =================
@app.route("/delete")
def delete():
    if os.path.exists("attendance.csv"):
        os.remove("attendance.csv")
    return "<h2>All data deleted</h2><a href='/admin'>Back</a>"

# ================= DOWNLOAD =================
@app.route("/download")
def download():
    if os.path.exists("attendance.csv"):
        return send_file("attendance.csv", as_attachment=True)
    return "No file"

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
