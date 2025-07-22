from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from config import SECRET_KEY

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DECRYPTED_FOLDER = "decrypted"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPTED_FOLDER, exist_ok=True)

BLOCK_SIZE = 16

def encrypt_file(data, key):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, BLOCK_SIZE))
    return cipher.iv + ct_bytes  # prepend IV

def decrypt_file(encrypted_data, key):
    iv = encrypted_data[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(encrypted_data[16:]), BLOCK_SIZE)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            data = file.read()
            encrypted = encrypt_file(data, SECRET_KEY)
            with open(os.path.join(UPLOAD_FOLDER, filename + '.enc'), 'wb') as f:
                f.write(encrypted)
            return redirect(url_for('index'))
    files = os.listdir(UPLOAD_FOLDER)
    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, 'rb') as f:
        encrypted_data = f.read()
    decrypted = decrypt_file(encrypted_data, SECRET_KEY)
    clean_name = filename.replace('.enc', '')
    dec_path = os.path.join(DECRYPTED_FOLDER, clean_name)
    with open(dec_path, 'wb') as f:
        f.write(decrypted)
    return send_from_directory(DECRYPTED_FOLDER, clean_name, as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))  # Render gives a PORT env variable
    app.run(host='0.0.0.0', port=port)         # Required for Render to run Flask

