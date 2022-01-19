from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os, secrets, time

load_dotenv() # loads env variables

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

UPLOAD_FOLDER = f'{os.getcwd()}/files/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_files():
    files = []

    for filename in os.listdir(UPLOAD_FOLDER):
        modificationTime = time.strftime('%Y-%m-%d | %H:%M:%S', time.localtime(os.path.getmtime(f'files/{filename}')))

        file = (filename, sizeof_fmt(os.path.getsize(f'files/{filename}')), modificationTime)
        files.append(file)

    return files

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in') is None:
        if request.method == 'POST':
            
            file = request.files['file']

            if os.path.isfile(UPLOAD_FOLDER + file.filename):
                flash('File already exists')
                return render_template('index.html', data=get_files())

            if file.filename == '':
                flash('No selected file')
                return render_template('index.html', data=get_files())

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                return render_template('index.html', data=get_files())

        else:
            return render_template('index.html', data=get_files())
    else:
        if request.method == 'POST':
            if request.form['passcode'] == os.getenv('PASSCODE'):
                session['logged_in'] = True
                return render_template('index.html', data=get_files())
            else:
                flash('Invalid Passcode')
                return render_template('index.html')
        else:
            return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    
    path = UPLOAD_FOLDER + filename

    if os.path.isfile(path):
        return send_file(path, as_attachment=True)
    else:
        return redirect(url_for('index'))

@app.route('/delete/<filename>')
def delete(filename):
    if os.path.isfile(UPLOAD_FOLDER + filename):
        os.remove(UPLOAD_FOLDER + filename)
        return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    if not os.path.isdir(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    app.run(debug=True)