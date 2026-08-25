#def create_dm_request(connection, sender, receiver):
#
#    cursor = connection.cursor()
#
#    cursor.execute(
#        """
#        SELECT id
#        FROM dm_requests
#        Where sender = ?
#        AND receiver = ?
#        AND status = 'pending'
#        """,
#        (sender, receiver)
#    )
#
#    existing_request = cursor.fetchhone()
#
#    if existing_request is not None:
#        return "DM request already exists"
#
#    cursor.execute(
#        """
#        INSERT INTO dm_requests(sender, reader, status)
#        VALUES (?, ?, ? 'pending')
#        """,
#        (sender, receiver)
#    )
#
#    connection.commit()
#
#    return "DM request sent"
#
#
#def get_dm_request(connection, sender, receiver):
#
#    cursor = connection.cursor()
#
#    cursor.execute(
#        """
#        SELECT id
#        FROM dm_requests
#        WHERE sender = ?
#        AND receiver = ?
#        AND status = 'pending'
#        """,
#        (sender, receiver)
#    )
#
#    return cursor.fetchone()
#
#
#def accept_dm_request(connection, sender, receiver):
#
#    request = get_dm_request(connection, sender, receiver)
#
#    if request is None:
#        return "DM request not found"
#
#    cursor = connection.cursor()
#
#    cursor.execute(
#        """
#        UPDATE dm_requests
#        SET status = 'accepted'
#        WGERE sender = ?
#        AND receiver = ?
#        AND status = 'pending'
#        """,
#        (sender, receiver)
#    )
#
#    connection.commit()
#
#    create_private_chat(connection, sender, receiver)
#
#    return "DM request accepted"
#
#
#
#
#def reject_dm_request(connection, sender, receiver):
#
#    request = get_dm_request(connection, sender, receiver)
#
#    if request is None:
#        return "DM request not found"
#
#    cursor = connection.cursor()
#
#    cursor.execute(
#        """
#        UPDATE dm_requests
#        SET status = 'rejected'
#        WHERE sender = ?
#        AND receiver = ?
#        AND status = 'pending'
#        """,
#        (sender,receiver)
#    )
#
#    connection.commit()
#
#    return "DM request rejected"
#





def get_private_chat_users(conversation_id, private_chats):
    
    return private_chats.get(conversation_id) 



def create_private_chat(user_1, user_2, private_chats):
    existing_chat = find_private_chat(user_1, user_2, private_chats)

    if existing_chat:
        return existing_chat

    conversation_id = f"dm_{len(private_chats) + 1}"

    private_chats[conversation_id] = [user_1, user_2]

    return conversation_id




def find_private_chat(user_1, user_2, private_chats):

    for conversation_id, users in private_chats.items():
        if user_1 in users and user_2 in users:
            return conversation_id

    return None



async def send_dm_message(conversation_id, sender, message, private_chats, nicknames):

    users = private_chats.get(conversation_id)

    if users is None:
        return

    for username in users:

        if username == sender:
            continue

        for writer, nickname in nicknames.items():

            if nickname == username:

                writer.write(f"[DM] {sender}: {message}\n".encode())
                await writer.drain() 




if __name__ == "__main__":
    private_chats = {
        "dm_1": ["Alice", "Bob"],
        "dm_2": ["Sachin", "John"]
    }

    print(find_private_chat("Alice", "Bob", private_chats))
    print(create_private_chat("Rahul", "Alex", private_chats))

    print(get_private_chat_users("dm_1", private_chats))
    print(get_private_chat_users("dm_2", private_chats))
    print(get_private_chat_users("dm_99", private_chats))