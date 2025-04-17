from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import unpad
from Crypto.Hash import HMAC, SHA1
import gzip
from typing import Union, Optional

def decrypt_es3(file_path: str, password: str) -> Union[str, bytes]:
    """
    Decrypts an .es3 save file.
    
    Args:
        file_path: Path to the .es3 file
        password: Password used for decryption
        
    Returns:
        Decrypted data as string or bytes
    """
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        # Extract the IV (first 16 bytes)
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]

        # Derive the key using PBKDF2
        key = PBKDF2(
            password, 
            iv, 
            dkLen=16, 
            count=100, 
            prf=lambda p, s: HMAC.new(p, s, SHA1).digest()
        )

        # Decrypt the data using AES-128-CBC
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)

        # Check if the data is GZip compressed
        if decrypted_data[:2] == b'\x1f\x8b':  # GZip magic number
            decrypted_data = gzip.decompress(decrypted_data)

        return decrypted_data
    except Exception as e:
        raise Exception(f"Error decrypting file: {str(e)}")

"""Funzioni per la decrittografia dei salvataggi"""

from .encryption import decrypt_save 