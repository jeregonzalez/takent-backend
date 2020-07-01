from flask_bcrypt import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password).decode('utf-8')


def check_password(hash_pw, password):
    return check_password_hash(hash_pw, password)
