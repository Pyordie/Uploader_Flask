from flask import Flask, render_template, request, send_file, abort
from flask_sqlalchemy import SQLAlchemy
import os
import secrets
from io import BytesIO

file_path = "sqlite:///" + os.path.abspath(os.path.join(os.getcwd(), "database.db"))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Upload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(50))
    data = db.Column(db.LargeBinary)
    key = db.Column(db.String(50))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload-file", methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        file = request.files['file']
        if file:
            password = secrets.token_urlsafe(16)  # Generate a secure random password
            upload = Upload(filename=file.filename, data=file.read(), key=password)
            db.session.add(upload)
            db.session.commit()
            return render_template("uploaded.html",filename=file.filename, password=password )
        else:
            abort(400, "No file provided")
    return render_template("upload_file.html")



@app.route("/download", methods=['POST','GET'])
def download():
    if request.method == "POST":
        password = request.form.get("password")
        if password:
            return get_access(password)
        else:
            abort(400, "No password provided")
    else:
        return render_template("download.html")
def get_access(password):
    download_file = Upload.query.filter_by(key=password).first()
    if download_file:
        return send_file(BytesIO(download_file.data), download_name=download_file.filename, as_attachment=True)
    else:
        file_not_found_message = "File not found"
        return render_template("download.html", file_not_found_message=file_not_found_message)

if __name__ == "__main__":
    app.run(debug=True)
