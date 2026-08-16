from server.database.connection import get_connection

#storage for chat history "connection"
def create_msg_table():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            conversation TEXT,
            timestamp TEXT
        )
    """)

    connection.commit()
    connection.close()



#function to save the chat in the DB
def save_message( sender, message, conversation):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (sender, message, conversation, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (sender, message, conversation))

    connection.commit()
    connection.close()



#function to retrieve the chat history from the DB
def get_messages(conversation):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages WHERE conversation = ? ORDER BY id ASC", (conversation,))
    messages = cursor.fetchall()
    connection.close()


    return messages





if __name__ == "__main__":
    create_msg_table()

    save_message("SK", "Hello V9", "general")

    message = get_messages("general")

    print(message)