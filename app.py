from flask import Flask
from flask import request

import os
from os.path import join, dirname
from dotenv import load_dotenv

from datetime import datetime

import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage

import json 
 
TIME_FMT = "%Y-%m-%dT%H:%M:%S"
FOLDER_NAME = 'backups'

app = Flask(__name__) 

@app.route('/')
def home():
   return 'Welcome to the auto-saver. Please visit Notes for Fronliners to write a note at ____'
  
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

      return data

   return 'Password entered: %s <br>Correct password: %s' % (password_entered, password)
  

if __name__ == '__main__': 
   dotenv_path = join(dirname(__file__), '.env')
   load_dotenv(dotenv_path)
   
   creds = credentials.Certificate("key.json")
   firebase_admin.initialize_app(
      credential=creds, 
      options={
         'databaseURL':'https://support-notes-for-frontliners.firebaseio.com/',
         'storageBucket':'support-notes-for-frontliners.appspot.com'
   })

   if not os.path.exists(FOLDER_NAME):
      os.mkdir(FOLDER_NAME)

   app.run()
