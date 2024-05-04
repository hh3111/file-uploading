from distutils.log import debug
from fileinput import filename
from flask import *
import os
from io import BytesIO
from db import get, create
from google.cloud import storage
from pathlib import Path
import datetime
import hashlib
app = Flask(__name__)

storage_client = storage.Client()
bucket_name = "ciphersquad-bucket"

@app.route('/')
def main():
    return render_template("login.html", )

@app.route('/verify', methods = ['POST'])
def verify():
    username = request.form.get('username')
    password = request.form.get('password')
    password = hashlib.sha256(password.encode()).hexdigest()
    attempt = get(username, password)
    if attempt:
        aid = attempt[0].get('id')
        buckets = storage_client.list_buckets()
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
        for blob in bucket.list_blobs():
            print(blob.metadata.get('Hash'))
        return render_template("index.html", username=attempt[0].get('username'), id=attempt[0].get('id'), blobs=bucket.list_blobs())
        print("Success")
    else:
        return render_template("login.html", fail=1)
        print("Failure")

@app.route('/login')
def login():
    return render_template("login.html", fail=2)

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']
        username = request.form.get('username')
        id = request.form.get('id')
        
        bucket = storage_client.get_bucket('cs-gy-6903-ciphersquad-' + str(id))
        blob = bucket.blob(f.filename)
        out_file = f.read()

        hashedfile = hashlib.sha256(out_file).hexdigest()
        print(hashedfile)
        now = str(datetime.datetime.now())
        metadata = {'Hash': hashedfile, 'Added': now}
        blob.metadata = metadata
        f.seek(0)
        blob.upload_from_file(f)

        return render_template("acknowledgement.html", name=f.filename)

@app.route('/add', methods = ['POST'])
def add_user():
    print(request.form)
    username = request.form.get('username')
    password = request.form.get('password')
    password = hashlib.sha256(password.encode()).hexdigest()
    create(username, password)
    return 'User Added'

@app.route('/download', methods = ['POST'])
def download_file():
    filename = request.form.get('file').replace('/', '')
    username = request.form.get('username').replace('/', '')
    id = request.form.get('id').replace('/', '')
    bucket_name = 'cs-gy-6903-ciphersquad-' + str(id)

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(filename)
    contents = blob.download_as_bytes()

    file_obj = BytesIO(contents)
    return send_file(file_obj, attachment_filename=filename, as_attachment=True)

@app.route('/delete', methods = ['POST'])
def delete():
    filename = request.form.get('file').replace('/', '')
    username = request.form.get('username').replace('/', '')
    id = request.form.get('id').replace('/', '')
    bucket_name = 'cs-gy-6903-ciphersquad-' + str(id)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(filename)

    blob.delete()

    return render_template("index.html", username=username, id=id, blobs=bucket.list_blobs())
    print("Success")

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)