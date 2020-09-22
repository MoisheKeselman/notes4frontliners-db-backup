from flask import Flask
from flask import request

import os
from os.path import join, dirname
from dotenv import load_dotenv
import base64
from binascii import hexlify

from datetime import datetime

import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage

import json 
 
TIME_FMT = "%Y-%m-%dT%H:%M:%S"
FOLDER_NAME = 'backups'

app = Flask(__name__) 


def generate_google_service(fileName):
    open(fileName, "w+").write(base64ToString(os.getenv("FIREBASE_SERVICE_CODE")))
    return fileName


def base64ToString(b):
    return base64.b64decode(bytes(b, "utf-8").decode('unicode_escape')).decode('utf-8')


@app.route('/')
def home():
   return 'Welcome to the database saver. Please visit <a href="https://notesforfrontliners.org/"> Notes for Fronliners</a> to write a note </a>'
  
@app.route('/save-db') 
def save_db(): 
   password_entered = request.args.get('pswd')
   password = os.environ.get("PASSWORD")
   
   if password == password_entered:
      data = db.reference('stats').get()  # TODO: change reference to be entire databases

      filename = f'{FOLDER_NAME}/{datetime.now().strftime(TIME_FMT)}.json'  # FOLDER_NAME is both the local and remote folder name
      open(filename, 'w').write(json.dumps(data))

      bucket = storage.bucket()  # get storage reference
      blob = bucket.blob(filename)  # create blob
      blob.upload_from_filename(filename)  # upload it

      return 'Data saved :)'

   return 'Incorrect password'
  

if __name__ == '__main__': 
   dotenv_path = join(dirname(__file__), '.env')
   load_dotenv(dotenv_path)
   
   key_filename = 'key2.json'
   generate_google_service(key_filename)

   creds = credentials.Certificate(key_filename)
   firebase_admin.initialize_app(
      credential=creds, 
      options={
         'databaseURL':'https://support-notes-for-frontliners.firebaseio.com/',
         'storageBucket':'support-notes-for-frontliners.appspot.com'
   })

   if not os.path.exists(FOLDER_NAME):
      os.mkdir(FOLDER_NAME)

   port = int(os.environ.get('PORT', 5000))
   app.run(host='0.0.0.0', port=port)
