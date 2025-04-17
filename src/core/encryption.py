"""Save file encryption functions"""

import os
import json
import logging
import gzip
from typing import Dict, Any, Union, List
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import HMAC, SHA1

from .error_handler import EncryptionError, DataError

logger = logging.getLogger(__name__)

def decrypt_es3(file_path, password):
    """
    Decrypt an ES3 file using the original algorithm
    
    Args:
        file_path: File path
        password: Decryption password
        
    Returns:
        bytes: Decrypted data
    """
    try:
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()

        logger.debug(f"Data received: {len(encrypted_data)} bytes")
        
        # Extract the IV (first 16 bytes)
        iv = encrypted_data[:16]
        encrypted_data = encrypted_data[16:]
        
        iv_hex = iv.hex()
        logger.debug(f"Extracted IV: {iv_hex}")
        logger.debug(f"Encrypted data: {encrypted_data[:100].hex()}...")
        
        # Ensure password is string type
        if isinstance(password, bytes):
            password = password.decode('utf-8')
            
        # Derive the key using PBKDF2
        key = PBKDF2(password, iv, dkLen=16, count=100, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())
        logger.debug("Key derived successfully")
        
        # Decrypt the data using AES-128-CBC
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data), AES.block_size)
        
        # Check if the data is GZip compressed
        if decrypted_data[:2] == b'\x1f\x8b':  # GZip magic number
            decrypted_data = gzip.decompress(decrypted_data)
        
        return decrypted_data
    except Exception as e:
        logger.error(f"Error during decryption: {str(e)}")
        raise

def encrypt_es3(data, password, should_gzip=False):
    """
    Encrypt data using the original algorithm
    
    Args:
        data: Data to encrypt
        password: Encryption password
        should_gzip: Whether to compress the data with GZip
        
    Returns:
        bytes: Encrypted data
    """
    if should_gzip:
        data = gzip.compress(data)

    iv = os.urandom(16)
    
    # Ensure password is string type
    if isinstance(password, bytes):
        password = password.decode('utf-8')

    key = PBKDF2(password, iv, dkLen=16, count=100, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data, AES.block_size))

    return iv + encrypted_data

def encrypt_save(data: Union[Dict[str, Any], str], password: Union[str, bytes] = "REPO") -> bytes:
    """
    Encrypt a save file
    
    Args:
        data: Data to encrypt (dictionary or JSON string)
        password: Encryption password
        
    Returns:
        bytes: Encrypted data
    """
    try:
        # Convert data to JSON if it's a dictionary
        if isinstance(data, dict):
            json_data = json.dumps(data)
        else:
            json_data = data
            
        # Encrypt the data
        return encrypt_es3(json_data.encode('utf-8'), password, should_gzip=False)
    
    except json.JSONDecodeError as e:
        logger.error(f"Error during JSON encoding: {str(e)}")
        raise DataError(
            "Error during data encoding",
            f"Unable to encode data to JSON: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error during encryption: {str(e)}")
        raise EncryptionError(
            "Error during encryption",
            f"Unable to encrypt data: {str(e)}"
        )

def decrypt_save(file_path: Union[str, Path], password: Union[str, bytes] = "Why would you want to cheat?... :o It's no fun. :') :'D") -> Dict[str, Any]:
    """
    Decrypt a save file
    
    Args:
        file_path: File path
        password: Decryption password
        
    Returns:
        Dict[str, Any]: Decrypted data
    """
    passwords_to_try = [
        "Why would you want to cheat?... :o It's no fun. :') :'D",
        "REPO",
        "ES3"
    ]
    
    # If a specific password was provided, try it first
    if password != "Why would you want to cheat?... :o It's no fun. :') :'D" and password not in passwords_to_try:
        passwords_to_try.insert(0, password)
    
    errors = []
    
    for pwd in passwords_to_try:
        try:
            # Decrypt the data
            decrypted_data = decrypt_es3(file_path, pwd)
            
            # Convert to dictionary
            try:
                result = json.loads(decrypted_data.decode('utf-8'))
                logger.info(f"Decryption successful with password: {pwd}")
                return result
            except json.JSONDecodeError as e:
                errors.append(f"Password {pwd}: JSON Error: {str(e)}")
                continue
        except Exception as e:
            errors.append(f"Password {pwd}: {str(e)}")
            continue
    
    # If we get here, no password worked
    error_msg = "\n".join(errors)
    logger.error(f"Error during decryption with all passwords:\n{error_msg}")
    raise EncryptionError(
        "Error during decryption",
        "Unable to decrypt data: Invalid data: The data may be corrupted or not a valid save"
    )

# Alias for compatibility with save_manager.py
def decrypt_data(file_path: Union[str, Path, bytes]) -> Dict[str, Any]:
    """
    Alias for decrypt_save that handles both paths and binary data
    
    Args:
        file_path: File path or binary data to decrypt
        
    Returns:
        Dict[str, Any]: Decrypted data
    """
    # If the parameter is already a path, use decrypt_save directly
    if isinstance(file_path, (str, Path)) and not isinstance(file_path, bytes):
        return decrypt_save(file_path)
    
    # If it's binary data, save it to a temporary file and then use decrypt_save
    elif isinstance(file_path, bytes):
        temp_file = Path("temp_decrypt.es3")
        try:
            with open(temp_file, 'wb') as f:
                f.write(file_path)
            return decrypt_save(temp_file)
        finally:
            if temp_file.exists():
                temp_file.unlink()
    else:
        raise TypeError("The parameter must be a path or binary data")

def encrypt_data(data: Dict[str, Any]) -> bytes:
    """
    Alias for encrypt_save
    
    Args:
        data: Data to encrypt
        
    Returns:
        bytes: Encrypted data
    """
    return encrypt_save(data)
