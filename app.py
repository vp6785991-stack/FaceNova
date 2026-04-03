from flask import Flask, request, redirect, send_file
import os, csv
from datetime import datetime
import matplotlib.pyplot as plt

app = Flask(__name__)

# --------- SETUP ---------
if not os.path.exists("data"):
    os.makedirs("data")

CSV_FILE = "data/data.csv"

# --------- STYLE ---------
STYLE = """
<style>
body {
    margin:0;
    font-family:sans-serif;
    color:white;
    text-align:center;
    background: linear-gradient(rgba(0,0,0,0.6), rgba(0,0,0,0.8)),
    url("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5");
    background-size: cover;
}
.container {
    margin:20px;
    padding:20px;
    background:rgba(0,0,0,0.6);
    border-radius:20px;
    backdrop-filter: blur(15px);
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
input {
    padding:8px;
    border-radius:8px;
}
img {
    border-radius:10px;
    margin:10px;
}
</style>
"""

# --------- HOME ---------
@app.route("/")
def home():
    return f"""
    {STYLE}
    <h1>🚀 FaceNova Ultra PRO</h1>
    <div class="container">
    <form action="/capture" method="post" enctype="multipart/form-data">
        <input type="text" name="name" placeholder="Enter Name" required><br><br>
        <input type="file" name="photos" multiple required><br><br>
        <button type="submit">📸 Scan Faces</button>
    </form>

    <br>
    <a href="/admin"><button>⚙️ Admin</button></a>
    <a href="/guide"><button>📖 Guide</button></a>
    </div>
    """

# --------- MULTIPLE UPLOAD ---------
@app.route("/capture", methods=["POST"])
def capture():
    files = request.files.getlist("photos")
    name = request.form.get("name", "User")

    saved_images = ""

    for photo in files:
        if photo.filename == "":
            continue

        filename = f"data/{name}_{datetime.now().strftime('%H%M%S%f')}.jpg"
        photo.save(filename)

        saved_images += f'<img src="/img/{filename.split("/")[-1]}" width="120">'

        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([name, datetime.now().strftime("%d-%m-%Y"), datetime.now().strftime("%H:%M:%S")])

    return f"""
    {STYLE}
    <h2>✅ Upload Successful</h2>
    <p>{name}, {len(files)} images saved!</p>
    {saved_images}
    <br><br>
    <a href="/"><button>Go Home</button></a>
    """

# --------- ADMIN ---------
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
    <h1>⚙️ Admin Panel</h1>
    <div class="container">
    <table border="1" style="margin:auto;">
    <tr><th>Name</th><th>Date</th><th>Time</th></tr>
    {rows}
    </table>

    <br>
    <a href="/gallery"><button>🖼 Gallery</button></a>
    <a href="/graph"><button>📊 Graph</button></a>
    <a href="/download"><button>⬇ CSV</button></a>
    <a href="/delete"><button>🗑 Reset</button></a>
    <a href="/"><button>Home</button></a>
    </div>
    """

# --------- GALLERY ---------
@app.route("/gallery")
def gallery():
    imgs = ""
    for f in os.listdir("data"):
        if f.endswith(".jpg"):
            imgs += f'<img src="/img/{f}" width="120">'

    return f"""
    {STYLE}
    <h1>📸 Gallery</h1>
    <div class="container">
    {imgs}
    <br>
    <a href="/admin"><button>Back</button></a>
    </div>
    """

@app.route("/img/<path:filename>")
def img(filename):
    return send_file(f"data/{filename}")

# --------- GRAPH ---------
@app.route("/graph")
def graph():
    data = {}

    if os.path.exists(CSV_FILE):
        with open(CSV_FILE) as f:
            reader = csv.reader(f)
            for r in reader:
                data[r[0]] = data.get(r[0], 0) + 1

    plt.figure()
    plt.bar(data.keys(), data.values())
    plt.savefig("data/graph.png")

    return f"""
    {STYLE}
    <h1>📊 Analytics</h1>
    <div class="container">
    <img src="/graph-img" width="300">
    <br><br>
    <a href="/admin"><button>Back</button></a>
    </div>
    """

@app.route("/graph-img")
def graph_img():
    return send_file("data/graph.png")

# --------- GUIDE ---------
@app.route("/guide")
def guide():
    return f"""
    {STYLE}
    <h1>📖 How to Use</h1>
    <div class="container">
    Enter name → upload multiple photos → scan<br><br>
    Admin panel → check data<br>
    Gallery → view images<br>
    Graph → analytics<br>
    </div>
    <a href="/"><button>Back</button></a>
    """

# --------- DOWNLOAD ---------
@app.route("/download")
def download():
    return send_file(CSV_FILE, as_attachment=True)

# --------- DELETE ---------
@app.route("/delete")
def delete():
    if os.path.exists(CSV_FILE):
        os.remove(CSV_FILE)

    for f in os.listdir("data"):
        os.remove(f"data/{f}")

    return redirect("/admin")

# --------- RUN ---------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
