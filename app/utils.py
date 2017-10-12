from hashlib import sha256


def passwordHash(password):
    passwordBytes = password.encode('utf-8')
    return sha256(passwordBytes).hexdigest()
