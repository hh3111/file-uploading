from distutils.log import debug
from fileinput import filename
from flask import *
import os
from google.cloud import storage
app = Flask(__name__)

storage_client = storage.Client()
bucket_name = "ciphersquad-bucket"
bucket = storage_client.get_bucket(bucket_name)
print(f"Bucket {bucket.name} accessed.")

@app.route('/')
def main():
    


    return render_template("index.html", blobs=bucket.list_blobs())

@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        f = request.files['file']

        #for blob in bucket.list_blobs():
        #    print(blob.name)
        #    print(blob.id)
        blob = bucket.blob(f.filename)
        blob.upload_from_file(f)
        return render_template("acknowledgement.html", name=f.filename, dir=os.listdir())
        #return render_template("acknowledgement.html", name='hello', dir=os.listdir())

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=8080, debug=True)