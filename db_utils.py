import sqlite3

def init_db():
    connection = sqlite3.connect("user.db")
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user(
            id integer primary key autoincrement,
            username text unique not null,
            password_hash text not null,
            api_key text not null
    )
""")
    connection.commit()
    connection.close()

def insert_user(username, password_hash, api_key):
    # Insert a new user into the database
    connection = sqlite3.connect("user.db")
    cursor = connection.cursor()
    try:
        cursor.execute("insert into user (username, password_hash, api_key) values (?, ?, ?)",
        (username, password_hash, api_key))
        connection.commit()
        return True
    except sqlite3.IntegrityError:
        return False # username already exists
    finally:
        connection.close()

def get_user_credentials(username):
    # Retrieve user credentials (password_hash and api_key) from the database
    connection = sqlite3.connect("user.db")
    cursor = connection.cursor()
    cursor.execute("select password_hash, api_key from user where username = ?",(username,))
    result = cursor.fetchone()
    connection.close()
    return result

if __name__ == "__main__":
    init_db()