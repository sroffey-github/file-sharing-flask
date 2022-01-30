from unittest import result
from dotenv import load_dotenv
import sqlite3, os, hashlib

load_dotenv()

DB_PATH = os.getenv('DB_PATH')

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute('SELECT * FROM Users')
results = c.fetchall()
if results:
    for i in results:
        print(i)
else:
    print('[-] No Users')

name = input('Name: ')

passcode = input('Passcode: ')
passcode = hashlib.sha256(passcode.encode()).hexdigest()

for i in results:
    if passcode in i:
        print('[!] Account exists')
        exit()

admin = input('Admin (1 or 0): ')

c.execute('INSERT INTO Users(Name, Passcode, Admin) VALUES(?, ?, ?)', (name, passcode, admin))
conn.commit()

print('[+] User Added')