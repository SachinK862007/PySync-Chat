#from server.services.room_service import get_rooms
from server.services.room_service import join_room
from server.services.room_service import leave_room
from server.services.dm_service import find_private_chat
from server.services.dm_service import create_private_chat
from server.services.request_service import create_request
from server.services.request_service import respond_to_request



COMMANDS = {
    "/help",
    "/rooms",
    "/users",
    "/join",
    "/dm",
    "/accept",
    "/reject",
    "/leave",
    "/exit"
}


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

    if not room_name:
        return "Usage : /join <room_name>"

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

    if not user_2:
        return "Usage : /dm <user_name>"

    conversation_id = find_private_chat(user_1, user_2, private_chats)

    if conversation_id:
        return f"Conversation already exists: {conversation_id}"

    created = create_request(user_1, user_2, requests)

    if created:
        return f"DM request sent to {user_2}"

    return f"DM request to {user_2} already exists"



def handle_accept(receiver, sender, requests, private_chats):

    if not sender:
        return "Usage : /accept <user_name>"

    accepted = respond_to_request(sender, receiver, "accept", requests)

    if not accepted:
        return f"No pending DM request from {sender}"

    conversation_id = create_private_chat(sender, receiver, private_chats)

    return f"DM request from {sender} accepted. Conversation: {conversation_id}"
    



def handle_reject(receiver, sender, requests):

    if not sender:
        return "Usage : /reject <user_name>"

    rejected = respond_to_request(sender, receiver, "reject", requests)
    if rejected:
        return f"DM request from {sender} rejected"

    return f"No pending DM request from {sender}"



def handle_exit():
    choice = input("Do you confirm exit (YES) or (NO) : ")

    if choice.upper() == "YES":
        return "exit"

    return "cancel"




def validate_command(command):

    if command not in COMMANDS:
        return False

    return True



def dispatch_command(command, argument, writer, users, rooms, private_chats, requests):
    pass

    #if command == "/help":
    #    return handle_help()
#
    #if command == "/rooms":
    #    return handle_rooms()
#
    #if command == "/users":
    #    return handle_users()
#
    #if command == "/join":
    #    return handle_join(argument)
#
    #if command == "/leave":
    #    return handle_leave()
#
    #if command == "/dm":
    #    return handle_dm(argument)
#
    #if command == "/accept":
    #    return handle_accept(argument)
#
    #if command == "/reject":
    #    return handle_reject(argument)
#
    #if command == "/exit":
    #    return handle_exit()
#
    #return "Unknown command"




def parse_command(message):
    parts = message.split(maxsplit = 1)

    command = parts[0].lower()

    argument = None

    if len(parts) > 1:
        argument = parts[1]

    return command, argument









if __name__ == "__main__":

    print("\n---- Testing Command Validation ----")

    print(validate_command("/join"))
    print(validate_command("/dm"))
    print(validate_command("/help"))

    print(validate_command("/hello"))
    print(validate_command("/random"))

    print("\n")

    command, argument = parse_command("/hello Sachin")

    print("Command:", command)
    print("Argument:", argument)
    print("Valid:", validate_command(command))