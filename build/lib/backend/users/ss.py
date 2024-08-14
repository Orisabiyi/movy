from cryptography.fernet import Fernet

# Generate a key and instantiate a Fernet instance
key = Fernet.generate_key()
print(key)
cipher_suite = Fernet(key)
token = cipher_suite.encrypt("kelanidarasimi9@gmail.com".encode()).decode()
print(token)
print(cipher_suite.decrypt(token.encode()))