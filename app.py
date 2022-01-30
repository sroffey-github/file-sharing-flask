from distutils.command.upload import upload
from unittest import result
from flask import Flask, render_template, request, flash, redirect, send_file, url_for, session
from sqlalchemy import false
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os, secrets, time, sqlite3, hashlib

load_dotenv() # loads env variables

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

UPLOAD_FOLDER = f'{os.getcwd()}/files/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
DB_PATH = os.getenv('DB_PATH')

def init():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('CREATE TABLE IF NOT EXISTS Users(id INTEGER PRIMARY KEY, Name TEXT, Passcode TEXT, Admin INTEGER)')

    conn.commit()

def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_files(name):
    files = []

    if os.path.isdir(UPLOAD_FOLDER + name) != True:
        os.mkdir(f'{UPLOAD_FOLDER}{name}')

    for filename in os.listdir(f'{UPLOAD_FOLDER}{name}'):
        modificationTime = time.strftime('%Y-%m-%d | %H:%M:%S', time.localtime(os.path.getmtime(f'files/{name}/{filename}')))

        file = (filename, sizeof_fmt(os.path.getsize(f'files/{name}/{filename}')), modificationTime)
        files.append(file)

    return files

def is_authorized(passcode):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    passcode = hashlib.sha256(passcode.encode()).hexdigest()
    c.execute('SELECT Name FROM Users WHERE Passcode = ?', (passcode,))
    results = c.fetchone()

    if results:
        return results[0]
    else:
        return False

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in') is None:
        if request.method == 'POST':
            
            file = request.files['file']

            if os.path.isfile(UPLOAD_FOLDER + session['username'] + '/' + file.filename):
                flash('File already exists')
                return render_template('index.html', data=get_files(session['username']))

            if file.filename == '':
                flash('No selected file')
                return render_template('index.html', data=get_files(session['username']))

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(UPLOAD_FOLDER + session['username'], filename))
                return render_template('index.html', data=get_files(session['username']))

            else:
                flash('An Error Occured')
                return render_template('index.html', data=get_files(session['username']))

        else:
            return render_template('index.html', data=get_files(session['username']))
    else:
        if request.method == 'POST':
            auth = is_authorized(request.form['passcode'])
            if auth != False: # request.form['passcode'] == os.getenv('PASSCODE') 
                session['username'] = auth
                session['logged_in'] = True
                return render_template('index.html', data=get_files(auth))
            else:
                flash('Access Denied')
                return render_template('index.html')
        else:
            return render_template('index.html')

@app.route('/download/<username>/<filename>')
def download_file(username, filename):

    if session['username'] == username:
    
        path = UPLOAD_FOLDER + username + '/' + filename

        if os.path.isfile(path):
            return send_file(path, as_attachment=True)
        else:
            return redirect(url_for('index'))
    else:
        return render_template('403.html'), 403

@app.route('/delete/<username>/<filename>')
def delete(username, filename):

    if session['username'] == username:

        if os.path.isfile(UPLOAD_FOLDER + username + '/' + filename):
            os.remove(UPLOAD_FOLDER + username + '/' + filename)
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))
    
    else:
        return render_template('403.html'), 403

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
    init()
    app.run(debug=True)