from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import os
import base64

"""def generate_key():
    # Generate a random 32-byte key
    key = os.urandom(32)
    
    # Optionally, encode the key in base64 for easier storage
    encoded_key = base64.urlsafe_b64encode(key)
    
    # Save the key to a file
    with open("secret.key", "wb") as key_file:
        key_file.write(encoded_key)
    
    return encoded_key"""

"""
def read_key():
    # Read the key from the file
    with open("secret.key", "rb") as key_file:
        encoded_key = key_file.read()
        #print(encoded_key)
    
    return base64.urlsafe_b64decode(encoded_key)
"""
def read_key():
    # Read the key from the file
    encoded_key=b'hC1VjfYRonv3V84y4VMcS9mPxgtun7sKmB8OiPJEOFw='
        #print(encoded_key)
    
    return base64.urlsafe_b64decode(encoded_key)


def texto_encriptado_credenciales(text):
    key = read_key()
    
    # Create a fixed IV (Initialization Vector)
    iv = b'0000000000000000'  # 16 bytes IV for AES
    
    # Initialize the cipher with AES algorithm, fixed IV, and CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Pad the text to ensure it's a multiple of block size
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(text.encode()) + padder.finalize()

    # Encrypt the padded text
    encrypted_text = encryptor.update(padded_data) + encryptor.finalize()

    # Encode the result as base64 to get a readable string
    encrypted_text_b64 = base64.b64encode(encrypted_text).decode('utf-8')
    
    return encrypted_text_b64




def decrypt_text_credenciales(encrypted_text_b64):
    key = read_key()
    
    # Create a fixed IV (Initialization Vector)
    iv = b'0000000000000000'  # 16 bytes IV for AES
    
    # Initialize the cipher with AES algorithm, fixed IV, and CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Decode the base64 encoded encrypted text
    encrypted_text = base64.b64decode(encrypted_text_b64)
    
    # Decrypt the text
    decrypted_padded_text = decryptor.update(encrypted_text) + decryptor.finalize()

    # Unpad the decrypted text
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted_text = unpadder.update(decrypted_padded_text) + unpadder.finalize()
    
    return decrypted_text.decode('utf-8')


def decrypt_list(encrypted_list):
    decrypted_list = [decrypt_text_credenciales(encrypted_value) for encrypted_value in encrypted_list]
    return decrypted_list


def encrypt_list(encrypted_list):
    decrypted_list = [texto_encriptado_credenciales(encrypted_value) for encrypted_value in encrypted_list]
    return decrypted_list


