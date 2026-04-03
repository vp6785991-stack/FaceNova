from flask import Flask, request, redirect, send_file
import os, csv
from datetime import datetime
from PIL import Image
import matplotlib.pyplot as plt

app = Flask(__name__)

if not os.path.exists("data"):
    os.makedirs("data")

CSV_FILE = "data/data.csv"

# ----------- GLOBAL STYLE -----------
STYLE = """
<style>
body {
    margin:0;
    font-family:sans-serif;
    background: linear-gradient(135deg,#0f172a,#1e293b);
    color:white;
    text-align:center;
}
.container {
    margin:20px;
    padding:20px;
    background:rgba(255,255,255,0.05);
    border-radius:15px;
    backdrop-filter: blur(10px);
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
    transform:scale(1.05);
}
a {text-decoration:none;}
img {border-radius:10px;}
</style>
"""

# ----------- HOME -----------
@app.route("/")
def home():
    return f"""
    {STYLE}
    <h1>🚀 FaceNova Ultra PRO</h1>
    <div class="container">
    <form action="/capture" method="post" enctype="multipart/form-data">
        <input type="text" name="name" placeholder="Enter Name" required><br><br>
        <input type="file" name="photo" required><br><br>
        <button type="submit">📸 Scan Face</button>
    </form>

    <br>
    <a href="/admin"><button>⚙️ Admin Panel</button></a>
    <a href="/guide"><button>📖 Guide</button></a>
    </div>
    """

# ----------- CAPTURE -----------
@app.route("/capture", methods=["POST"])
def capture():
    name = request.form["name"]
    photo = request.files["photo"]

    filename = f"data/{name}_{datetime.now().strftime('%H%M%S')}.jpg"
    photo.save(filename)

    date = datetime.now().strftime("%d-%m-%Y")
    time = datetime.now().strftime("%H:%M:%S")

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, date, time])

    return redirect("/")

# ----------- ADMIN -----------
@app.route("/admin")
def admin():
    rows = ""
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.reader(f)
            for r in reader:
                rows += f"<tr><td>{r[0]}</td><td>{r[1]}</td><td>{r[2]}</td></tr>"

    return f"""
    {STYLE}
    <h1>⚙️ Admin Dashboard</h1>
    <div class="container">
    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date</th><th>Time</th></tr>
    {rows}
    </table>

    <br>
    <a href="/graph"><button>📊 Analytics</button></a>
    <a href="/gallery"><button>🖼️ Gallery</button></a>
    <a href="/download"><button>⬇️ CSV</button></a>
    <a href="/delete"><button>🗑️ Reset</button></a>
    <a href="/guide"><button>📖 Guide</button></a>
    <a href="/"><button>🏠 Home</button></a>
    </div>
    """

# ----------- GALLERY -----------
@app.route("/gallery")
def gallery():
    imgs = ""
    for file in os.listdir("data"):
        if file.endswith(".jpg"):
            imgs += f'<img src="/img/{file}" width="120" style="margin:10px;">'

    return f"""
    {STYLE}
    <h1>📸 Smart Gallery</h1>
    <div class="container">
    {imgs}
    <br>
    <a href="/admin"><button>Back</button></a>
    </div>
    """

@app.route("/img/<path:filename>")
def img(filename):
    return send_file(f"data/{filename}")

# ----------- GRAPH -----------
@app.route("/graph")
def graph():
    names = {}

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.reader(f)
            for r in reader:
                names[r[0]] = names.get(r[0], 0) + 1

    plt.figure()
    plt.bar(names.keys(), names.values())
    plt.savefig("data/graph.png")

    return f"""
    {STYLE}
    <h1>📊 Analytics Dashboard</h1>
    <div class="container">
    <img src="/graph-img" width="300">
    <br><br>
    <a href="/admin"><button>Back</button></a>
    </div>
    """

@app.route("/graph-img")
def graph_img():
    return send_file("data/graph.png")

# ----------- GUIDE -----------
@app.route("/guide")
def guide():
    return f"""
    {STYLE}
    <h1>📖 How to Use FaceNova</h1>
    <div class="container">
    <h3>Step 1:</h3> Enter your name<br>
    <h3>Step 2:</h3> Upload photo<br>
    <h3>Step 3:</h3> Click Scan Face<br>
    <h3>Step 4:</h3> Data saved automatically<br>

    <h3>Admin Features:</h3>
    View users, analytics, gallery & download CSV

    <br><br>
    <a href="/"><button>Back</button></a>
    </div>
    """

# ----------- DOWNLOAD CSV -----------
@app.route("/download")
def download():
    return send_file(CSV_FILE, as_attachment=True)

# ----------- DELETE -----------
@app.route("/delete")
def delete():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

    for f in os.listdir("data"):
        if f.endswith(".jpg") or f.endswith(".png"):
            os.remove(f"data/{f}")

    return redirect("/admin")

# ----------- RUN -----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
