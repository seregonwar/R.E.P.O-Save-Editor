from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Util.Padding import pad
from Crypto.Hash import HMAC, SHA1
import gzip
import os

def encrypt_es3(data, output_file, password, should_gzip=False):
    """Cripta e salva i dati in un file
    
    Args:
        data: Dati da criptare (stringa o bytes)
        output_file: Percorso dove salvare il file criptato
        password: Password per la criptazione
        should_gzip: Se True, comprime i dati con gzip prima della criptazione
        
    Returns:
        bool: True se il salvataggio è andato a buon fine, False altrimenti
    """
    try:
        # Converti in bytes se è una stringa
        if isinstance(data, str):
            data = data.encode('utf-8')
            
        # Compress the data if required
        if should_gzip:
            data = gzip.compress(data)

        # Generate a random IV
        iv = os.urandom(16)

        # Derive the key using PBKDF2
        key = PBKDF2(password, iv, dkLen=16, count=100, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())

        # Encrypt the data using AES-128-CBC
        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted_data = cipher.encrypt(pad(data, AES.block_size))

        # Prepend the IV to the encrypted data
        result = iv + encrypted_data
        
        # Salva il risultato nel file
        with open(output_file, 'wb') as f:
            f.write(result)
            
        return True
    except Exception as e:
        print(f"Errore durante la criptazione o il salvataggio: {str(e)}")
        return False

