def get_private_chat_users(conversation_id, private_chats):
    
    return private_chats.get(conversation_id) 



def create_private_chat(user_1, user_2, private_chats):
    existing_chat = find_private_chat(user_1, user_2, private_chats)

    if existing_chat:
        return existing_chat

    conversation_id = f"dm_{len(private_chats) + 1}"

    private_chats[conversation_id] = [user_1, user_2]

    return conversation_id




def find_private_chat(user_1, user_2, private_chat):

    for conversation_id, users in private_chats.items():
        if user_1 in users and user_2 in users:
            return conversation_id

    return None




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