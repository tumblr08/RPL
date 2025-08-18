import hashlib

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_password(pw, hashed):
    return hash_password(pw) == hashed
