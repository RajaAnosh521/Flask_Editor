from flask import Flask, render_template, request, flash
import os
import logging
from werkzeug.utils import secure_filename
import cv2

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'webp', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'  # Add this line

# Ensure the upload and static folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)

# Set up logging
logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ProcessImage(filename, operation):
    print(f"The operation is {operation} and filename is {filename}") 
    img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    processed_filename = os.path.join('static', filename)
    if operation == "cgray":
        imgProcessed = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif operation == "cwebp":
        processed_filename = processed_filename.rsplit('.', 1)[0] + '.webp'
        imgProcessed = img
    elif operation == "cjpg":
        processed_filename = processed_filename.rsplit('.', 1)[0] + '.jpg'
        imgProcessed = img
    elif operation == "cpng":
        processed_filename = processed_filename.rsplit('.', 1)[0] + '.png'
        imgProcessed = img
    else:
        imgProcessed = img

    cv2.imwrite(processed_filename, imgProcessed)
    return processed_filename

@app.route("/")
def main():
    app.logger.info('Home route accessed')
    return render_template('index.html')

@app.route("/About")
def about():
    return render_template('about.html')

@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":
        operation = request.form.get("operation")
        app.logger.debug("POST request received")
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            app.logger.debug("No file part in request")
            return render_template('index.html')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            app.logger.debug("No selected file")
            return render_template('index.html')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            app.logger.debug(f"File {filename} saved successfully")
            processed_filename = ProcessImage(filename, operation)
            flash(f"Your image has been processed and is available <a href='/{processed_filename}' target='_blank'>here</a>")
            return render_template('index.html')
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=5001)
