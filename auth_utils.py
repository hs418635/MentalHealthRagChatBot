import bcrypt
import sqlite3
from db_utils import init_db, insert_user, get_user_credentials

def register_user(username, password, api_key):
    # hash the password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    success = insert_user(username, password_hash, api_key)
    return success

def authenticate_user(username, password):
    # Authenticate a user by checking their hashed password
    credentials = get_user_credentials(username)
    if credentials:
        password_hash, api_key = credentials
        if bcrypt.checkpw(password.encode('utf-8'), password_hash):
            return api_key
    return None

if __name__ == "__main__":
    # Initialize the database
    init_db()

    # test user registration and authentication
    username = 'test_user'
    password = "password123"
    api_key = "sk-test-api-key"

    # register a new user
    if register_user(username, password, api_key):
        print("user registered successfully")

    # Authenticate the user
    api_key_from_login = authenticate_user(username, password)
    if api_key_from_login:
        print("Login successful! API Key:", api_key_from_login)
    else:
        print("Login failed.")
