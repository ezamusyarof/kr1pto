from flask import Flask, render_template, request, send_file, redirect, url_for
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

app = Flask(__name__)

def generate_key(key_filename='key.key'):
    key = os.urandom(16)
    with open(key_filename, 'wb') as key_file:
        key_file.write(key)

def encrypt_file(content, key):
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    with open('plaintext.txt', 'w') as file:
        file.write(content)
    
    with open('plaintext.txt', 'rb') as file:
        data = file.read()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    with open('encrypted_file', 'wb') as file:
        file.write(iv)
        file.write(encrypted_data)
    
    os.remove("plaintext.txt")

def decrypt_file(input_filename, key):
    with open(input_filename, 'rb') as file:
        iv = file.read(16)
        encrypted_data = file.read()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())

    decryptor = cipher.decryptor()
    decrypted_padded_data = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted_data = unpadder.update(decrypted_padded_data) + unpadder.finalize()

    with open('decrypted_file.txt', 'wb') as file:
        file.write(decrypted_data)

# Fungsi Flask
@app.route('/', methods=['GET', 'POST'])
def index():
    generate_key()
    if request.method == 'POST':
        text = request.form.get('teks')
        
        key = open('key.key', 'rb').read()
        encrypt_file(text, key)

    return render_template('index.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    content = ""
    if request.method == 'POST':
        cipher = request.files['cipher']
        private_key = request.files['privkey']
        
        cipher_file = cipher.filename
        key = private_key.filename

        key = open(key, 'rb').read()
 
        decrypt_file(cipher_file, key)

        # return 'File berhasil didekripsi dan disimpan!'
    
        with open("decrypted_file.txt", "r") as file:
            content = file.read()
    
    return render_template('decrypt.html', content=content)

@app.route('/download', methods=['GET','POST'])
def download():
    if request.method == 'POST':
        download = request.form.get("butt")

        if download == 'down_cipher':
            for file in os.listdir():
                if file.startswith("encrypted_"):               
                    return send_file(file, as_attachment=True)
                
        elif download == 'down_privkey':
            return send_file('key.key', as_attachment=True)

    return redirect(url_for("index"))

@app.route('/about')
def about():
    return render_template('aboutus.html')

if __name__ == '__main__':
    # generate_key()
    app.run(debug=True)
