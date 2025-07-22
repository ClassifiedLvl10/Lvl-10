import hashlib

password = "class16497"
SECRET_KEY = hashlib.sha256(password.encode()).digest()
