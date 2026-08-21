import sqlite3


#storage for chat history "connection"
def connect_db():
    connection = sqlite3.connect("pysync_chat.db")
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
    return connection



#function to save the chat in the DB
def save_message(connection, sender, message, conversation):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (sender, message, conversation, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (sender, message, conversation))

    connection.commit()

#function to retrieve the chat history from the DB
def get_messages(connection, conversation):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages WHERE conversation = ? ORDER BY id ASC", (conversation,))
    messages = cursor.fetchall()
    return messages



if __name__ == "__main__":
    connection = connect_db()

    save_message(
        connection,
        "SK",
        "Database test message",
        "general"
    )

    history = get_messages(
        connection,
        "general"
    )

    print(history)

    connection.close()