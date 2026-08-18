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



def dispatch_command(command, argument, writer, current_user, users, rooms, private_chats, requests):

    if command == "/help":
        return handle_help()

    if command == "/rooms":
        return handle_rooms(rooms)

    if command == "/users":
        return handle_users(users)

    if command == "/join":
        return handle_join(writer, argument, rooms)

    if command == "/leave":
        return handle_leave(writer, rooms)

    if command == "/dm":
        return handle_dm(current_user, argument, private_chats, requests)

    if command == "/accept":
        return handle_accept(current_user, argument, requests, private_chats)

    if command == "/reject":
        return handle_reject(current_user, argument, requests)

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



    users = {
        "Sachin": "writer_1",
        "John": "writer_2",
        "Deku": "writer_3"
    }

    rooms = {
        "general": [],
        "scuba": []
    }

    private_chats = {}

    requests = []

    writer = "writer_1"

    current_user = "Sachin"




    print("\n========== TEST /help ==========")

    print(handle_help())


    print("\n========== TEST /users ==========")

    print(handle_users(users))


    print("\n========== TEST /rooms ==========")

    print(handle_rooms(rooms))




    print("\n========== TEST /join ==========")

    print(
        handle_join(
            writer,
            "scuba",
            rooms
        )
    )




    print("\n========== TEST /join duplicate ==========")

    print(
        handle_join(
            writer,
            "scuba",
            rooms
        )
    )




    print("\n========== TEST /leave ==========")

    print(
        handle_leave(
            writer,
            rooms
        )
    )




    print("\n========== TEST /leave again ==========")

    print(
        handle_leave(
            writer,
            rooms
        )
    )




    requests = []
    private_chats = {}

    print("\n========== TEST /dm ==========")

    print(
        handle_dm(
            "Sachin",
            "John",
            private_chats,
            requests
        )
    )

    print("Requests:", requests)




    print("\n========== TEST /dm duplicate ==========")

    print(
        handle_dm(
            "Sachin",
            "John",
            private_chats,
            requests
        )
    )

    print("Requests:", requests)




    requests = [
        {
            "sender": "Sachin",
            "receiver": "John",
            "status": "pending"
        }
    ]

    private_chats = {}

    print("\n========== TEST /accept ==========")

    print(
        handle_accept(
            "John",
            "Sachin",
            requests,
            private_chats
        )
    )

    print("Requests:", requests)
    print("Private chats:", private_chats)




    requests = [
        {
            "sender": "Sachin",
            "receiver": "John",
            "status": "pending"
        }
    ]

    print("\n========== TEST /reject ==========")

    print(
        handle_reject(
            "John",
            "Sachin",
            requests
        )
    )

    print("Requests:", requests)




    print("\n========== TEST /exit ==========")

    result = handle_exit()

    print("Result:", result)




    print("\n========== TEST ARGUMENT VALIDATION ==========")

    print(
        handle_join(
            writer,
            "",
            rooms
        )
    )

    print(
        handle_dm(
            "Sachin",
            "",
            private_chats,
            requests
        )
    )

    print(
        handle_accept(
            "John",
            "",
            requests,
            private_chats
        )
    )

    print(
        handle_reject(
            "John",
            "",
            requests
        )
    )




    print("\n========== TEST COMMAND PARSER ==========")

    print(
        parse_command("/join scuba")
    )

    print(
        parse_command("/dm John")
    )

    print(
        parse_command("/accept Sachin")
    )

    print(
        parse_command("/rooms")
    )

    print(
        parse_command("/help")
    )

    print(
        parse_command("/join my room")
    )




    print("\n========== TEST COMMAND VALIDATION ==========")

    print(
        validate_command("/help")
    )

    print(
        validate_command("/join")
    )

    print(
        validate_command("/dm")
    )

    print(
        validate_command("/exit")
    )

    print(
        validate_command("/hello")
    )

    print(
        validate_command("/random")
    )




    print("\n========== TEST PARSER + VALIDATOR ==========")

    command, argument = parse_command("/join scuba")

    print("Command:", command)
    print("Argument:", argument)
    print("Valid:", validate_command(command))


    command, argument = parse_command("/hello Sachin")

    print("Command:", command)
    print("Argument:", argument)
    print("Valid:", validate_command(command))




    print("\n========== DISPATCHER /help ==========")

    print(
        dispatch_command(
            "/help",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    print("\n========== DISPATCHER /rooms ==========")

    print(
        dispatch_command(
            "/rooms",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    print("\n========== DISPATCHER /users ==========")

    print(
        dispatch_command(
            "/users",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    print("\n========== DISPATCHER /join ==========")

    print(
        dispatch_command(
            "/join",
            "scuba",
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    print("\n========== DISPATCHER /leave ==========")

    print(
        dispatch_command(
            "/leave",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    requests = []

    print("\n========== DISPATCHER /dm ==========")

    print(
        dispatch_command(
            "/dm",
            "John",
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print("Requests:", requests)




    requests = [
        {
            "sender": "Sachin",
            "receiver": "John",
            "status": "pending"
        }
    ]

    private_chats = {}

    print("\n========== DISPATCHER /accept ==========")

    print(
        dispatch_command(
            "/accept",
            "Sachin",
            "writer_2",
            "John",
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print("Requests:", requests)
    print("Private chats:", private_chats)




    requests = [
        {
            "sender": "Sachin",
            "receiver": "John",
            "status": "pending"
        }
    ]

    print("\n========== DISPATCHER /reject ==========")

    print(
        dispatch_command(
            "/reject",
            "Sachin",
            "writer_2",
            "John",
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print("Requests:", requests)




    print("\n========== DISPATCHER /exit ==========")

    result = dispatch_command(
        "/exit",
        None,
        writer,
        current_user,
        users,
        rooms,
        private_chats,
        requests
    )

    print("Result:", result)




    print("\n========== DISPATCHER ARGUMENT VALIDATION ==========")

    print(
        dispatch_command(
            "/join",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print(
        dispatch_command(
            "/dm",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print(
        dispatch_command(
            "/accept",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )

    print(
        dispatch_command(
            "/reject",
            None,
            writer,
            current_user,
            users,
            rooms,
            private_chats,
            requests
        )
    )




    print("\n========== UNKNOWN COMMAND ==========")

    command, argument = parse_command("/hello Sachin")

    if not validate_command(command):
        print("Unknown command:", command)
    else:
        print(
            dispatch_command(
                command,
                argument,
                writer,
                current_user,
                users,
                rooms,
                private_chats,
                requests
            )
        )


    print("\n==========================================")
    print("       ALL TESTS FINISHED")
    print("==========================================")