#from server.services.room_service import get_rooms
from server.services.room_service import join_room
from server.services.room_service import leave_room
from server.services.dm_service import find_private_chat


def handle_help():
    
    return """
    Available commands :

    /help
    /join <room>
    /users
    /rooms
    /dm <username>
    /accept <username>
    /reject <username>
    /leave
    /exit
    """


def handle_users(users):
    return list(users.keys())



def handle_rooms(rooms):
    return list(rooms.keys())


def handle_join(writer, room_name, rooms):

    joined = join_room(writer, room_name, rooms)

    if not joined:
        return f"You are already in #{room_name}"

    return f"You joined #{room_name}"


def handle_leave(writer, rooms):
    room_name = leave_room(writer, rooms)

    if not room_name is None:
        return "You are not in the room"

    return f"You left #{room_name}"



def handle_dm(user_1, user_2, private_chats):
    conversation_id = find_private_chat(user_1, user_2, private_chats)

    if conversation_id:
        return f"Conversation already exists: {conversation_id}"

    return None



if __name__ == "__main__":
    user_1 = "Sachin"
    user_2 = "Alice"

    private_chats = {
        "dm_1": ["Sachin", "Alice"],
        "dm_2": ["John", "Rahul"]
    }

    requests = []

    print(handle_dm(user_1, user_2, private_chats, requests))
    print(requests)

    print(handle_dm("Sachin", "John", private_chats, requests))
    print(requests)

    print(handle_dm("Sachin", "John", private_chats, requests))
    print(requests)