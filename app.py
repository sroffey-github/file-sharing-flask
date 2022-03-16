from flask import Flask, render_template, request, flash, redirect, send_file, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import controller
import time
import uuid
import os

load_dotenv()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/download/<filename>')
def download_file(filename):
    return send_file(UPLOAD_FOLDER + '//' + filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete(filename):
    if os.path.isfile(UPLOAD_FOLDER + '//' + filename):
        os.remove(UPLOAD_FOLDER + '//' + filename)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if request.form['submitBtn'] == 'Upload':
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url, data=controller.get_files())

            file = request.files['file']
            
            if file.filename in os.listdir(UPLOAD_FOLDER):
                flash('Error, File Already Exists!')
                return render_template('index.html', data=controller.get_files())

            if file.filename == '':
                flash('Error, No selected file')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                flash('Success, File Uploaded Successfully.')
                return render_template('index.html', files=controller.get_files())
        elif request.form['submitBtn'] == 'Search':
            q = request.form['query']
            results = controller.search(q)
            if results:
                number = len(results)
                return render_template('index.html', data=results, number=number)
            else:
                flash('Error, no results found.')
                return render_template('index.html')
    else:
        return render_template('index.html', data=controller.get_files())

if __name__ == '__main__':
    app.run(debug=True)