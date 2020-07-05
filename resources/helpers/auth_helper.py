from flask_bcrypt import generate_password_hash, check_password_hash


def hash_password(password):
    """
    Dada una password pasada como parametro, crea un hash
    :param password:
    :return: Password hasheada
    """
    return generate_password_hash(password).decode('utf-8')


def check_password(hash_pw, password):
    """
    Verifica que una password y su hash sean correctas
    :param hash_pw:
    :param password:
    :return: bool
    """
    return check_password_hash(hash_pw, password)
