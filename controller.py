from dotenv import load_dotenv
import os, time

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

def human_readable_size(size, decimal_places=2):
    for unit in ['B','KiB','MiB','GiB','TiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f}{unit}"

def get_files():
    files = []
    
    for i in os.listdir(UPLOAD_FOLDER):
        name = i
        created = time.ctime(os.path.getctime(UPLOAD_FOLDER + '//' + i))
        modified = time.ctime(os.path.getmtime(UPLOAD_FOLDER + '//' + i))
        size = human_readable_size(os.path.getsize(UPLOAD_FOLDER + '//' + i))
        files.append((name, created, modified, size))
    
    return files

def search(q):
    results = []
    
    files = get_files()
    
    for i in files:
        if q in i:
            results.append(i)
            
    return results