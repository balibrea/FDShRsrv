import os
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Base paths for every FD
FD_PATHS = {
    "LL": "/Raid/data/Fd/FD-LosLeones/eyepc",
    "LM": "/Raid/data/Fd/FD-LomaAmarilla/eyepc",
    "LA": "/Raid/data/Fd/FD-LosMorados/eyepc",
    "CO": "/Raid/data/Fd/FD-Coihueco/eyepc",
    "HE": "/Raid/data/Fd/FD-Heat/eyepc",
}

@app.route("/")
def index():
    return render_template("run-test.html", fds=FD_PATHS.keys())

@app.route("/list_days/<fd>/<year>/<month>")
def list_days(fd, year, month):
    """List available days for a given FD"""
    base_path = os.path.join(FD_PATHS[fd], year, month)
    try:
        days = sorted(os.listdir(base_path))
    except FileNotFoundError:
        days = []
    return jsonify(days)

@app.route("/list_files/<fd>/<year>/<month>/<day>")
def list_files(fd, year, month, day):
    """List all files for a given FD and date"""
    base_path = os.path.join(FD_PATHS[fd], year, month, day, "data")
    try:
        files = sorted(os.listdir(base_path))
    except FileNotFoundError:
        files = []
    return jsonify(files)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
