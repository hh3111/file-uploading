from distutils.log import debug
from fileinput import filename
from flask import *
import os
from io import BytesIO
from db import get, create
from google.cloud import storage
from pathlib import Path
#from functools import partial
import hashlib
app = Flask(__name__)

storage_client = storage.Client()
bucket_name = "ciphersquad-bucket"
#bucket = storage_client.get_bucket(bucket_name)
#blobs=bucket.list_blobs()
#print(f"Bucket {bucket.name} accessed.")

@app.route('/')
def main():
    return render_template("login.html", )

@app.route('/verify', methods = ['POST'])
def verify():
    username = request.form.get('username')
    password = request.form.get('password')
    password = hashlib.sha256(password.encode()).hexdigest()
    attempt = get(username, password)
    aid = attempt[0].get('id')
    if attempt:
        buckets = storage_client.list_buckets()
        #print('cs-gy-6903-ciphersquad-' + str(aid))
        #for bucket in buckets:
        #    print(bucket.name)
        bucketexists = 0
        bucket_name = 'cs-gy-6903-ciphersquad-' + str(aid)
        for bucket in buckets:
            if (bucket_name) == bucket.name:
                bucketexists = 1
        if bucketexists == 1:
            bucket = storage_client.get_bucket(bucket_name)
            print(f"Bucket {bucket.name} accessed")
        else:
            bucket = storage_client.bucket(bucket_name)
            new_bucket = storage_client.create_bucket(bucket, location="us")
            print(f"Created bucket {new_bucket.name}")
            
        print("Metadata Hash:")
        for blob in bucket.list_blobs():
            print(blob.metadata.get('Hash'))
        return render_template("index.html", username=attempt[0].get('username'), id=attempt[0].get('id'), blobs=bucket.list_blobs())
        print("Success")
    else:
        return render_template("register.html")
        print("Failure")
    #return get(username, password)
    #return render_template("index.html", user=username)
    #return get()

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        username = request.form.get('username')
        id = request.form.get('id')
        #for blob in bucket.list_blobs():
        #    print(blob.name)
        #    print(blob.id)

        #print(hashlib.sha256(contents).hexdigest())

        
        bucket = storage_client.get_bucket('cs-gy-6903-ciphersquad-' + str(id))
        blob = bucket.blob(f.filename)
        contents = blob.download_as_bytes()
        hashedfile = hashlib.sha256(contents).hexdigest()
        metadata = {'Hash': hashedfile}
        blob.metadata = metadata
        blob.upload_from_file(f)
        return render_template("acknowledgement.html", name=f.filename)
        #return render_template("acknowledgement.html", name='hello', dir=os.listdir())

@app.route('/add', methods = ['POST'])
def add_user():
    print(request.form)
    username = request.form.get('username')
    password = request.form.get('password')
    password = hashlib.sha256(password.encode()).hexdigest()
    #if not useradd.is_json:
    #    return jsonify({"add": "Missing JSON"}), 400
    #create("test", "test")
    create(username, password)
    return 'User Added'

@app.route('/download', methods = ['POST'])
def download_file():
    filename = request.form.get('file').replace('/', '')
    username = request.form.get('username').replace('/', '')
    id = request.form.get('id').replace('/', '')
    bucket_name = 'cs-gy-6903-ciphersquad-' + str(id)
    destination = '/'

    

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    #blob.download_to_filename('/tmp/' + filename)
    contents = blob.download_as_bytes()

    file_obj = BytesIO(contents)
    #return send_from_directory(full_path, filename)
    return send_file(file_obj, attachment_filename=filename, as_attachment=True)

    #send_from_directory(app.config['DOWNLOAD_FOLDER'], filename, as_attachment=True)
    
    return render_template("index.html", username=username, id=id, blobs=bucket.list_blobs())

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)