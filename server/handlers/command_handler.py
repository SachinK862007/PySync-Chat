#from server.services.room_service import get_rooms
from server.services.room_service import join_room
from server.services.room_service import leave_room
from server.services.dm_service import find_private_chat
from server.services.dm_service import create_private_chat
from server.services.request_service import create_request
from server.services.request_service import respond_to_request


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

    if room_name is None:
        return "You are not in the room"

    return f"You left #{room_name}"



def handle_dm(user_1, user_2, private_chats,requests):
    conversation_id = find_private_chat(user_1, user_2, private_chats)

    if conversation_id:
        return f"Conversation already exists: {conversation_id}"

    created = create_request(user_1, user_2, requests)

    if created:
        return f"DM request sent to {user_2}"

    return f"DM request to {user_2} already exists"



def handle_accept(receiver, sender, requests, private_chats):
    accepted = respond_to_request(sender, receiver, "accept", requests)

    if not accepted:
        return f"No pending DM request from {sender}"

    conversation_id = create_private_chat(sender, receiver, private_chats)

    return f"DM request from {sender} accepted. Conversation: {conversation_id}"
    



def handle_reject(receiver, sender, requests):
    rejected = respond_to_request(sender, receiver, "reject", requests)
    if rejected:
        return f"DM request from {sender} rejected"

    return f"No pending DM request from {sender}"



def handle_exit():
    choice = input("Do you confirm exit (YES) or (NO) : ")

    if choice.upper() == "YES":
        return "exit"

    return "cancel"
    




if __name__ == "__main__":
    requests = [
        {
            "sender": "Sachin",
            "receiver": "John",
            "status": "pending"
        }
    ]

    private_chats = {}

    print(handle_accept(
        "John",
        "Sachin",
        requests,
        private_chats
    ))

    print(requests)
    print(private_chats)

    result = handle_exit()

    print("Result:", result)

    assert result == "exit"

    print("Test passed")