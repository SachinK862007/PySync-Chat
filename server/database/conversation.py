from server.database.connection import get_connection

def create_connection_table():
    
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()



if __name__ == '__main__':
    create_connection_table()
    print("connection table created successfully !")