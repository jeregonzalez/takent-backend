from flask_bcrypt import generate_password_hash, check_password_hash


def hash_password(password):
    return generate_password_hash(password).decode('utf-8')


def check_password(self, password):
    return check_password_hash(self.password, password)
