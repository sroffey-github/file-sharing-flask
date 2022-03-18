import os
from dotenv import load_dotenv
import os

load_dotenv()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER')

for i in range(20):
    f = open(f'{UPLOAD_FOLDER}/testfile({str(i)}).txt', 'w')
    f.close()