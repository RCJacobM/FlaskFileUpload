from flask import Flask, render_template, request, send_from_directory
from wtforms import FileField, SubmitField, StringField, TextAreaField
from flask_wtf import FlaskForm
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image, ImageFilter
from dotenv import load_dotenv
import qrcode
import waitress
import logging
import socket
import subprocess
import os
import base64
import hashlib
import sqlite3
from filename import createFilename
from splash import message

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["upload_folder"] = os.path.join(app.root_path, "static", "uploads")
app.config["resource_folder"] = os.path.join(app.root_path, "static", "resource")
app.config["splash_message_file"] = os.path.join(app.config["resource_folder"], "messages.json")
app.config["mainpage"] = "index.html"
app.config["respage"] = "response.html"

class UploadForm(FlaskForm): 
    file = FileField("File")
    submit = SubmitField("Upload!")
    text = StringField("")

@app.route("/", methods=["GET", "POST"])
def home():
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data # Get the file
        print(file)
        hasher = hashlib.sha256()
        while True:
            chunk = file.stream.read(8388608) # 8mb
            if not chunk:
                break
            hasher.update(chunk)
        hex = hasher.hexdigest()
        file.stream.seek(0)
        try:
            newFilename = createFilename(file.filename, hex)
            file.save(os.path.join(app.config["upload_folder"], secure_filename(newFilename)))
        except:
            return render_template(app.config["respage"], code="NOFILE"), 400 # ERR | No file submitted
        
        link = f"{request.host_url}uploads/{newFilename}"

        qr = qrcode.QRCode(version=1, box_size=50, border=0) # initialize qrcode object
        qr.add_data(link) # add data to qr
        qr.make(fit=True)

        with qr.make_image(fill_color="#000000", back_color="#FFFFFF").resize((200, 200), resample=Image.NEAREST).filter(ImageFilter.SHARPEN) as img: # create the qrcode
            buf = BytesIO() 
            img.save(buf, format="PNG") # save the qrcode in memory
            imgByts = buf.getvalue() # get the bytes from the image
            imgB64 = base64.b64encode(imgByts).decode('utf-8') # encode the bytes
            qrRes = f"data:image/png;base64,{imgB64}" # turn it into a data url

        return render_template(app.config["respage"],link=link, code= "SUCCESS", qrRes=qrRes, form=form) # SUCCESS
    
    return render_template(app.config["mainpage"], form=form, msg=message(app.config["splash_message_file"]))

@app.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(app.config["upload_folder"], filename)

texts = ['None']
@app.route("/clipboard", methods=["GET", "POST"])
def clipboard():
    global texts
    form = UploadForm()
    if form.validate_on_submit():
        text = form.text.data
        texts.append(text)
        subprocess.run("clip", text=True, input=text)
        return render_template("clipboard.html", form=form, text=texts[-1])
    
    # if request.method == "POST":
    #     text = request.form.get("text")
    #     subprocess.run("clip", text=True, input=text)
    
    return render_template("clipboard.html", form=form, text=texts[-1])

# if __name__ == "__main__":
#     app.run(debug=True, host="0.0.0.0", port=8080)

host = socket.gethostbyname(socket.gethostname())
if __name__ == "__main__":
    logger = logging.getLogger("waitress")
    logger.setLevel(logging.INFO)
    waitress.serve(app, port=8080, host=host, threads=2, max_request_body_size=1073741824*2)