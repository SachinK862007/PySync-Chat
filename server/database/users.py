from server.database.connection import get_connection

def create_users_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT UNIQUE NOT NULL
        )
    """)

    connection.commit()
    connection.close()



if __name__ == "__main__":
    create_users_table()
    print("users table created successfully.")