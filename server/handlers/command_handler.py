#from server.services.room_service import get_rooms

from server.services.room_service import join_room
from server.services.room_service import leave_room

from server.services.dm_service import find_private_chat
from server.services.dm_service import create_private_chat

from server.services.request_service import create_request
from server.services.request_service import respond_to_request
from server.services.request_service import get_requests_for_users



COMMANDS = {
    "/help",
    "/rooms",
    "/users",
    "/join",
    "/dm",
    "/requests",
    "/accept",
    "/reject",
    "/leave",
    "/dmleave",
    "/where",
    "/exit"
}


def handle_help():
    
    return """
    Available commands :

    /help
    /join <room>
    /users
    /rooms
    /requests
    /dm <username>
    /accept <username>
    /reject <username>
    /leave
    /dmleave
    /where
    /exit
    """


def handle_users(writer, rooms, nicknames):
    current_room = None

    for room_name, clients in rooms.items():
        if writer in clients:
            current_room = room_name
            break

    if current_room is None:
        return "You are not in a room.\n"

    users_message = f"Users in {current_room}\n"

    for client in rooms[current_room]:
        users_message += f"{nicknames[client]}\n"

    return users_message



def handle_rooms(rooms):
    rooms_message = "Available Rooms\n"

    for room_name in rooms:
        rooms_message += f"{room_name}\n"

    return rooms_message


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
        return f"Switched to DM with {conversation_id}"

    created = create_request(user_1, user_2, requests)

    if created:
        return f"DM request sent to {user_2}"

    return f"DM request to {user_2} already exists"



def handle_requests(current_user, requests):

    user_requests = get_requests_for_user(current_user, requests)

    incoming = []
    sent = []

    for request in user_requests:

        if request["receiver"] == current_user:
            incoming.append(request)

        elif request["sender"] == current_user:
            send.append(request)

    result = ""

    if incoming:
        result += ("Incoming DM requests:\n")

        for request in incoming:
            result += (f"-from {request['sender']} : {request['status']}-\n")

    else:
        result += ("Incoming DM requests:\n""None\n")

    result += "\n"

    if sent:
        result += ("Sent DM requests:\n")

        for request in sent:

            result += (f"-to {request['receiver']} : {request['status']}\n")

    else:
        result += ("Sent DM requests:\n""None\n")

    return result



def handle_accept(receiver, sender, requests, private_chats):

    if not sender:
        return "Usage : /accept <user_name>"

    accepted = respond_to_request(sender, receiver, "accept", requests)

    if not accepted:
        return f"No pending DM request from {sender}"

    create_private_chat(sender, receiver, private_chats)

    return (
        f"DM request from {sender}"
        f"accepted. "
        f"You are now in a DM with {sender}"
    )
    



def handle_reject(receiver, sender, requests):

    if not sender:
        return "Usage : /reject <user_name>"

    rejected = respond_to_request(sender, receiver, "reject", requests)
    if rejected:
        return (
            f"DM request from"
            f"{sender} rejected"
        )

    return( 
        f"No pending DM request" 
        f"from {sender}"
    )



def handle_dmleave(writer, current_user, private_chats, active_dms):

    if writer not in active_dms:
        return("You are not in a DM")

    conversation_id = (active_dms[writer])

    users = private_chats.get(conversation_id)

    if users is None:
        return ("You are in an unkown DM")
    
    other_user = None

    for username in users:
        if username != current_user:

            other_user = username
            break

    if other_user is None:
        return ("You left the DM !")

    return f"You left DM with {other_user}"



def handle_where(writer, current_user, rooms, private_chats, active_dms):

    if writer in active_dms:
        conversation_id = (active_dms[writer])

        users = private_chats.get(conversation_id)

        if users is None:
            return "You are in unknown DM"

        other_user = None

        for username in users:
            if username != current_user:

                other_user = username
                break

        if other_user is None:

            return f"DM: {current_user}"

        return(
            f"DM: {current_user}"
            f"<-> {other_user}"
        )

    for room_name, clients in rooms.items():

        if writer in clients:
            return f"#{room_name}"

    return "You are not in a room or DM"




def handle_exit():
    return "exit"




def validate_command(command):

    if command not in COMMANDS:
        return False

    return True



def dispatch_command(command, argument, writer, current_user, users, rooms, private_chats, requests, active_dms = None):

    if command == "/help":
        return handle_help()

    if command == "/rooms":
        return handle_rooms(rooms)

    if command == "/users":
        return handle_users(writer, rooms, users)

    if command == "/join":
        return handle_join(writer, argument, rooms)

    if command == "/leave":
        return handle_leave(writer, rooms)

    if command == "/dm":
        return handle_dm(current_user, argument, private_chats, requests)

    if command == "requests":
        return handle_requests(current_user, requests)

    if command == "/accept":
        return handle_accept(current_user, argument, requests, private_chats)

    if command == "/reject":
        return handle_reject(current_user, argument, requests)

    if command =="/dmleave":
        return handle_dmleave(writer, current_user, private_chats, active_dms)

    if command == "/where":
        return handle_where(writer, current_user, rooms, active_dms)

    if command == "/exit":
        return handle_exit()

    return "Unknown command"




def parse_command(message):
    parts = message.split(maxsplit = 1)

    command = parts[0].lower()

    argument = None

    if len(parts) > 1:
        argument = parts[1]

    return command, argument









if __name__ == "__main__":

    print("Testing command handler...")

    command, argument = parse_command("/join scuba")

    print("Command:", command)
    print("Argument:", argument)

    print("Valid:", validate_command(command))