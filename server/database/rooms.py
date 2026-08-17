from server.database.connection import get_connection


def create_rooms_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    cursor.execute("""
        INSERT OR IGNORE INTO rooms (name)
        VALUES (?)
    """, ("general",))

    connection.commit()
    connection.close()



if __name__ == '__main__':
    create_rooms_table()
    print("rooms table created successfully !")