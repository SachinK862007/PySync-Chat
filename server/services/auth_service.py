from .database_service import connect_db

import hashlib
import os


def validate_username(username):

    if not username:
        return False

    if " " in username:
        return False

    return True 


def validate_password(password):

    if not password:
        return False

    if len(password) < 8:
        return False

    return True

def hash_password(password):

    salt = os.urandom(16)

    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)

    return salt.hex(), password_hash.hex()



def verify_password(password, salt, stored_hash):

    password_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100000)

    return password_hash.hex() == stored_hash



def register_user(connection, username, password):

    if not validate_username(username):
        return "Invalid username"

    if not validate_password(password):
        return "Invalid password"

    cursor = connection.cursor()

    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))

    existing_user = cursor.fetchone()

    if existing_user is not None:
        return "Username already exists"

    salt, password_hash = hash_password(password)

    cursor.execute(
        """
        INSERT INTO users (username, password_hash, salt)
        VALUES (?, ?, ?)
        """,
        (username, password_hash, salt)
    )

    connection.commit()

    return "Registration Successful !\n"





def login_user(connection, username, password):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT password_hash, salt
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        return "User not found"

    stored_hash, salt = user

    if not verify_password(password, salt, stored_hash):
        return "Invalid password"

    return "Login successful"




def get_user(connection, username):

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, username
        FROM users
        WHERE username = ?
        """,
        (username,)
    )

    user = cursor.fetchone()

    return user


def authenticate_user(connection, username, password):

    login_result = login_user(connection, username, password)

    if login_result != "Login successful":
        return None

    return get_user(connection, username)








if __name__ == "__main__":

    connection = connect_db()


    print("\n========== USERNAME VALIDATION ==========")

    print(validate_username("SK"))
    print(validate_username("Deku"))
    print(validate_username(""))
    print(validate_username("SK Gowda"))


    print("\n========== PASSWORD VALIDATION ==========")

    print(validate_password("password123"))
    print(validate_password("12345678"))
    print(validate_password("1234"))
    print(validate_password(""))


    print("\n========== PASSWORD HASHING ==========")

    salt1, hash1 = hash_password("password123")

    print("Salt:", salt1)
    print("Hash:", hash1)

    print("Salt length:", len(salt1))
    print("Hash length:", len(hash1))


    print("\n========== SALT TEST ==========")

    salt2, hash2 = hash_password("password123")

    print("Same salt:", salt1 == salt2)
    print("Same hash:", hash1 == hash2)


    print("\n========== PASSWORD VERIFICATION ==========")

    print(
        verify_password(
            "password123",
            salt1,
            hash1
        )
    )

    print(
        verify_password(
            "wrongpassword",
            salt1,
            hash1
        )
    )


    print("\n========== REGISTRATION ==========")

    print(
        register_user(
            connection,
            "TestUser",
            "password123"
        )
    )


    print(
        register_user(
            connection,
            "AnotherUser",
            "password456"
        )
    )


    print("\n========== DUPLICATE USERNAME ==========")

    print(
        register_user(
            connection,
            "TestUser",
            "anotherpassword"
        )
    )


    print("\n========== INVALID USERNAME ==========")

    print(
        register_user(
            connection,
            "Test User",
            "password123"
        )
    )


    print("\n========== INVALID PASSWORD ==========")

    print(
        register_user(
            connection,
            "ShortPassword",
            "1234"
        )
    )


    print("\n========== LOGIN ==========")

    print(
        login_user(
            connection,
            "TestUser",
            "password123"
        )
    )

    print(
        login_user(
            connection,
            "TestUser",
            "wrongpassword"
        )
    )

    print(
        login_user(
            connection,
            "UnknownUser",
            "password123"
        )
    )


    print("\n========== USER LOOKUP ==========")

    print(
        get_user(
            connection,
            "TestUser"
        )
    )

    print(
        get_user(
            connection,
            "UnknownUser"
        )
    )


    print("\n========== AUTHENTICATION ==========")

    print(
        authenticate_user(
            connection,
            "TestUser",
            "password123"
        )
    )

    print(
        authenticate_user(
            connection,
            "TestUser",
            "wrongpassword"
        )
    )

    print(
        authenticate_user(
            connection,
            "UnknownUser",
            "password123"
        )
    )


    print("\n========== DATABASE USERS ==========")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, password_hash, salt
        FROM users
    """)

    users = cursor.fetchall()

    for user in users:
        print(user)


    connection.close()