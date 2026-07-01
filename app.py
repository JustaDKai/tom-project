import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    if "." not in filename:
        return False

    extension = filename.rsplit(".", 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    files = os.listdir(app.config["UPLOAD_FOLDER"])
    return render_template("index.html", files=files)


@app.route("/upload", methods=["POST"])
def upload_file():
    print("UPLOAD ROUTE HIT")

    if "file" not in request.files:
        return "No file part in the request", 400

    file = request.files["file"]

    if file.filename == "":
        return "No file selected", 400

    if not allowed_file(file.filename):
        return "File type is not allowed. Please upload png, jpg, jpeg, or gif.", 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    return redirect(url_for("home"))


@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


@app.route("/health")
def health():
    return "OK"


@app.route("/devops")
def devops():
    return "Tom is learning DevOps"


if __name__ == "__main__":
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
