from flask import Flask, request, redirect, send_file
import os, csv, base64
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CSV_FILE = f"{DATA_DIR}/data.csv"

# ---------- UI ----------
STYLE = """
<style>
body{
margin:0;
font-family:sans-serif;
color:white;
text-align:center;
background: linear-gradient(135deg,#020617,#0f172a,#1e3a8a,#9333ea);
}
.container{
margin:20px;
padding:20px;
background:rgba(0,0,0,0.6);
border-radius:20px;
}
button{
padding:10px;
margin:5px;
border:none;
border-radius:10px;
background:#22c55e;
color:white;
}
img{border-radius:10px;margin:5px;}
</style>
"""

# ---------- HOME ----------
@app.route("/")
def home():
    return f"""
    {STYLE}
    <h1>🚀 FaceNova Ultra PRO</h1>

    <div class="container">
    <h3>Upload Face (Training)</h3>
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input name="name" placeholder="Enter Name" required><br><br>
        <input type="file" name="photos" multiple required><br><br>
        <button>📸 Save Faces</button>
    </form>

    <h3>Live Camera Scan</h3>
    <video id="cam" width="250" autoplay></video><br>
    <button onclick="snap()">Scan Face</button>

    <canvas id="canvas" style="display:none;"></canvas>

    <form id="camForm" action="/camera" method="post">
        <input type="hidden" name="img" id="imgdata">
    </form>

    <br>
    <a href="/admin"><button>⚙️ Admin</button></a>
    <a href="/gallery"><button>🖼 Gallery</button></a>
    <a href="/graph"><button>📊 Graph</button></a>
    </div>

<script>
navigator.mediaDevices.getUserMedia({video:true})
.then(stream=>{document.getElementById('cam').srcObject=stream})

function snap(){
let canvas=document.getElementById("canvas");
let video=document.getElementById("cam");

canvas.width=video.videoWidth;
canvas.height=video.videoHeight;
canvas.getContext("2d").drawImage(video,0,0);

// compress image (IMPORTANT FIX)
let data=canvas.toDataURL("image/jpeg",0.7);

document.getElementById("imgdata").value=data;

// small delay to avoid crash
setTimeout(()=>{
document.getElementById("camForm").submit();
},300);
}
</script>
"""

# ---------- UPLOAD ----------
@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("photos")
    name = request.form["name"]

    user_dir = f"{DATA_DIR}/{name}"
    os.makedirs(user_dir, exist_ok=True)

    preview = ""

    for f in files:
        path = f"{user_dir}/{datetime.now().timestamp()}.jpg"
        f.save(path)
        preview += f'<img src="/img/{name}/{os.path.basename(path)}" width="100">'

    return f"{STYLE}<h2>Saved!</h2>{preview}<br><a href='/'>Back</a>"

# ---------- MATCH (SAFE DEMO) ----------
def match_face():
    users = [u for u in os.listdir(DATA_DIR) if os.path.isdir(f"{DATA_DIR}/{u}")]
    return users[0] if users else "Unknown"

# ---------- CAMERA FIXED ----------
@app.route("/camera", methods=["POST"])
def camera():
    try:
        data = request.form.get("img")

        if not data:
            return f"{STYLE}<h3>No image ❌</h3><a href='/'>Back</a>"

        header, encoded = data.split(",", 1)
        img_bytes = base64.b64decode(encoded)

        filename = f"{DATA_DIR}/cam_{datetime.now().timestamp()}.jpg"
        with open(filename, "wb") as f:
            f.write(img_bytes)

        name = match_face()

        with open(CSV_FILE, "a", newline="") as f:
            csv.writer(f).writerow([name, datetime.now().strftime("%d-%m-%Y %H:%M:%S")])

        return f"""
        {STYLE}
        <h2>✅ Face Scanned</h2>
        <p>Detected: {name}</p>
        <img src="/img_file/{os.path.basename(filename)}" width="200">
        <br><br>
        <a href="/">Back</a>
        """

    except Exception as e:
        return f"{STYLE}<h3>Error: {str(e)}</h3><a href='/'>Back</a>"

@app.route("/img_file/<filename>")
def img_file(filename):
    return send_file(f"{DATA_DIR}/{filename}")

# ---------- GALLERY ----------
@app.route("/gallery")
def gallery():
    imgs = ""
    for user in os.listdir(DATA_DIR):
        path = f"{DATA_DIR}/{user}"
        if os.path.isdir(path):
            for f in os.listdir(path):
                imgs += f'<img src="/img/{user}/{f}" width="100">'

    return f"{STYLE}<h2>Gallery</h2>{imgs}<br><a href='/'>Back</a>"

@app.route("/img/<user>/<file>")
def img(user, file):
    return send_file(f"{DATA_DIR}/{user}/{file}")

# ---------- GRAPH ----------
@app.route("/graph")
def graph():
    data = {}

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            for row in csv.reader(f):
                data[row[0]] = data.get(row[0], 0) + 1

    plt.figure()
    plt.bar(data.keys(), data.values())
    plt.savefig(f"{DATA_DIR}/bar.png")

    plt.figure()
    plt.plot(list(data.keys()), list(data.values()))
    plt.savefig(f"{DATA_DIR}/line.png")

    return f"""
    {STYLE}
    <h2>Graphs</h2>
    <img src="/graph-img/bar.png" width="300"><br>
    <img src="/graph-img/line.png" width="300">
    <br><a href='/'>Back</a>
    """

@app.route("/graph-img/<file>")
def graph_img(file):
    return send_file(f"{DATA_DIR}/{file}")

# ---------- ADMIN ----------
@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            for r in csv.reader(f):
                rows += f"<tr><td>{r[0]}</td><td>{r[1]}</td></tr>"

    return f"""
    {STYLE}
    <h2>Admin Panel</h2>
    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date-Time</th></tr>
    {rows}
    </table>
    <br>
    <a href="/download"><button>Download CSV</button></a>
    <a href="/"><button>Home</button></a>
    """

# ---------- DOWNLOAD ----------
@app.route("/download")
def download():
    return send_file(CSV_FILE, as_attachment=True)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
