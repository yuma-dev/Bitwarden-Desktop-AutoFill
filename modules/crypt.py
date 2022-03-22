from cryptography.fernet import Fernet
import os

def debug(*objects):
    import modules.debug as debugging,sys
    debugging.printDebug(objects,args=sys.argv)

def load_key():
    """
    Loads the key named `secret.key` from the current directory or creates it.
    """
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key","wb") as f:
            f.write(key)
        
    else:
        with open("secret.key","rb") as f:
            key = f.read()
            
    return key

def encrypt_message(message):
    """
    Encrypts a message
    """
    key = load_key()
    encoded_message = message.encode()
    f = Fernet(key)
    encrypted_message = f.encrypt(encoded_message)

    return encrypted_message
    
def decrypt_message(encrypted_message):
    """
    Decrypts an encrypted message
    """
    key = load_key()
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message)

    return decrypted_message.decode()
