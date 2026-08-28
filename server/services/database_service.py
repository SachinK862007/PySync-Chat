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

    #cursor.execute("DROP TABLE IF EXISTS users")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
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



def get_dm_contacts(connection, username):

    cursor = connection.cursor()

    cursor.execute("""
        SELECT conversation
        FROM messages
        WHERE conversation LIKE 'dm|%|%'
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    contacts = []

    for row in rows:

        conversation = row[0]

        parts = conversation.split("|", 2)

        if len(parts) != 3:
            continue

        user_1 = parts[1]
        user_2 = parts[2]

        if user_1 == username:
            other_user = user_2

        elif user_2 == username:
            other_user = user_1

        else:
            continue

        if other_user not in contacts:
            contacts.append(other_user)

    return contacts



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