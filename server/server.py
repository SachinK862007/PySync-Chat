from .services.auth_service import login_user
from .services.auth_service import register_user
from .services.auth_service import get_user

from server.services.room_service import join_room
from server.services.room_service import leave_room

from .handlers.command_handler import dispatch_command

from .services.database_service import connect_db
from .services.database_service import save_message
from .services.database_service import get_messages

from .services.room_service import find_current_room

from .services.dm_service import get_private_chat_users
from .services.dm_service import find_private_chat
from .services.dm_service import send_dm_message

from .services.request_service import find_pending_request



import asyncio
from .config import HOST, PORT

connected_clients = []
nicknames = {}
private_chats = {}
requests = []
active_dms = {}
rooms = {
    "general": []
}




#3rd function
async def brodcast_to_room(room_name, message, sender = None):
    for client in rooms[room_name]:
        if sender is None or client != sender:
            client.write(message.encode())
            await client.drain()



#4th function
async def remove_client(writer):
    current_room = await find_current_room(writer, rooms)
    if current_room is not None:

        if writer in rooms[current_room]:
            rooms[current_room].remove(writer)

    if writer in active_dms:
        active_dms.pop(writer, None)

    if writer in connected_clients:
        connected_clients.remove(writer)
        nicknames.pop(writer,None)


async def send_reply(writer, reply):
    writer.write(f"{reply}\n".encode())
    await writer.drain()






async def authenticate_client(reader, writer, connection):

    await send_reply(writer, "Welcome to PySync Chat!")

    while True:

        await send_reply(writer, "Press ENTER to Login")

        await send_reply(writer, "Type R to Register")

        choice = await reader.readline()

        if not choice:
            return None

        choice = choice.decode().strip().upper()

        if choice == "":    #Login

            await send_reply(writer, "Username : ")

            username_data = await reader.readline()

            if not username_data:
                return None

            username = username_data.decode().strip()

            await send_reply(writer, "Password : ")

            password_data = await reader.readline()

            if not password_data:
                return None

            password = password_data.decode().strip()

            result = login_user(connection, username, password)

            if result == "Login successful":

                await send_reply(writer, "Login successful!")
                return username

            await send_reply(writer, result)

            continue

            

        elif choice == "R":

            await send_reply(writer, "Choose username:")

            username_data = await reader.readline()

            if not username_data:
                return None

            username = username_data.decode().strip()

            await send_reply(writer, "Choose password:")

            password_data = await reader.readline()

            if not password_data:
                return None

            password = password_data.decode().strip()

            result = register_user(connection, username, password)

            await send_reply(writer, result)

            if result == "Registration Successful !\n":
                return username

            continue


        else:
            await send_reply(writer, "Invalid option. Please press ENTER for Login or type R for Register.")

            continue


    



#main function that call above functions
async def handle_client(reader, writer, connection):

    username = await authenticate_client(reader, writer, connection)

    if username is None:
        return 
    
    connected_clients.append(writer)

    rooms["general"].append(writer)

    #nickname_data = await reader.readline()
    
    #nickname = nickname_data.decode().strip()
    
    nicknames[writer] = username
    
    print(f"{username} Connected to general room !")
    
    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            message = data.decode().strip()

            if message.lower().startswith("/join "):

                room_name = message.split(maxsplit = 1)[1]

                reply = dispatch_command(
                    "/join",
                    room_name,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                writer.write(f"{reply}\n".encode())
                await writer.drain()

                if reply.startswith("You are already"):
                    continue
                
                history = get_messages(connect_db(), room_name)

                if not history:
                   reply = "----No previous messages.----\n"
                   writer.write(reply.encode())
                   await writer.drain()
                else:
                    history_header = f"----Previous messages in {room_name}----\n"
                    writer.write(history_header.encode())
                    await writer.drain()


                    for row in history:
                        message_id, sender, message, conversation, timestamp = row
                        history_message = f"{sender} : {message}\n"
                        writer.write(history_message.encode())
                        await writer.drain()

                join_message = f"{nicknames[writer]} joined : {room_name}\n"

                await brodcast_to_room(room_name, join_message) # calls 3rd function
                
                continue
                
            current_room = await find_current_room(writer, rooms) #calls 1st function


            if message.upper() == "/HELP":

                reply = dispatch_command(
                    "/help",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                await send_reply(writer, reply) 

                continue

            if message.upper() == "/ROOMS":
                
                reply = dispatch_command(
                    "/rooms",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                await send_reply(writer, reply) 

                continue

            if message.upper() == "/USERS":
                reply = dispatch_command(
                    "/users",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                await send_reply(writer, reply) 

                continue




            if message.upper() == "/LEAVE":

                if writer in active_dms:

                    active_dms.pop(writer, None)

                    join_room(writer, "general", rooms)

                    reply = "You left the DM and returned to #general"
                    await send_reply(writer, reply)

                    continue

                current_room = None

                for room_name, clients in rooms.items():
                    if writer in clients:

                        current_room = room_name
                        break

                if current_room is not None:

                    leave_room(writer, rooms)

                join_room(writer, "general", rooms)

                reply = "You returned to #general"    

                await send_reply(writer, reply)

                continue





            if message.upper() == "/DM" or message.upper().startswith("/DM "):

                parts = message.split(maxsplit = 2)
            
                if len(parts) < 2:
                    reply = "Usage: /dm <nickname>\n"
                    await send_reply(writer, reply)
                    continue
            
                target_nickname = parts[1]
            
                if target_nickname.lower() == nicknames[writer].lower():
                    await send_reply(writer, "You cannot DM yourself")
                    continue

                target_writer = None
            
                for client, nickname in nicknames.items():
                
                    if nickname.lower() == target_nickname.lower():
                        target_writer = client
                        break
            
                if target_writer is None:
                    reply = f"User {target_nickname} not found!\n"
                    await send_reply(writer, reply)
                    continue
            
                reply = dispatch_command(
                    "/dm",
                    target_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                conversation_id = find_private_chat(nicknames[writer], target_nickname, private_chats)

                if conversation_id:
                    active_dms[writer] = conversation_id

                #save_message(connect_db(), nicknames[writer], private_message, dm_id)
                await send_reply(writer, reply)

                if conversation_id is None:

                    await send_reply(
                        target_writer,
                        f"{nicknames[writer]} "
                        f"sent to a DM request. "
                        f"Use /requests to view it. "
                    )
            
                continue


            
            if message.upper() == "/REQUESTS":

                reply = dispatch_command(
                    "/requests",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                await send_reply(writer, reply)

                continue
            



            if message.upper() == "/ACCEPT" or message.upper().startswith("/ACCEPT "):

                parts = message.split(maxsplit = 1)

                if len(parts) < 2:
                    reply = "Usage: /accept <nick_name>"
                    await send_reply(writer, reply)
                    continue

                sender_nickname = parts[1]

                pending_request = find_pending_request(sender_nickname, nicknames[writer], requests)

                reply = dispatch_command(
                    "/accept",
                    sender_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                if pending_request is not None and pending_request["status"] == "accepted":
                    conversation_id = find_private_chat(nicknames[writer], sender_nickname, private_chats)

                    if conversation_id:
                        active_dms[writer] = conversation_id

                        for client, nickname in nicknames.items():

                            if nickname == sender_nickname:
                                #active_dms[client] = conversation_id

                                await send_reply(
                                    client,
                                    f"{nicknames[writer]} "
                                    f"accepted your DM request. "
                                    f"Use /dm "
                                    f"{nicknames[writer]} "
                                    f"to enter the conversation. "
                                )

                                break


                await send_reply(writer, reply)

                continue




            if message.upper() == "/REJECT" or message.upper().startswith("/REJECT "):

                parts = message.split(maxsplit = 1)

                if len(parts) < 2:
                    reply = "Usage: /reject <nick_name>"
                    await send_reply(writer, reply)
                    continue

                sender_nickname = parts[1]

                pending_request = find_pending_request(sender_nickname, nicknames[writer], requests)


                reply = dispatch_command(
                    "/reject",
                    sender_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                if pending_request is not None and pending_request["status"] == "rejected":
                    for client, nickname in nicknames.items():

                        if nickname == sender_nickname:
                            await send_reply(client, f"{nicknames[writer]} rejected your DM request.")
                            break

                await send_reply(writer, reply)

                continue




            if message.upper() == "/DMLEAVE":

                reply = dispatch_command(
                    "/dmleave",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                if writer in active_dms:
                    active_dms.pop(writer, None)

                await send_reply(writer, reply)

                continue


            
            if message.upper() == "/WHERE":

                reply = dispatch_command(
                    "/where",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                await send_reply(writer, reply)

                continue





            if message.upper() == '/EXIT':
                
                reply = dispatch_command(
                    "/exit",
                    writer,
                    None,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests,
                    active_dms
                )

                if reply == "exit":
                    break

                await send_reply(writer, reply)

                continue



            if current_room is None:
                reply = "You are not in a room.\n" 
                writer.write(reply.encode())
                await writer.drain()
                continue


            
            if writer in active_dms:

                conversation_id = active_dms[writer]

                await send_dm_message(conversation_id, nicknames[writer], message, private_chats, nicknames)

                continue



            #connect_db()
            save_message(connection, nicknames[writer], message, current_room)

            broadcast_message = f"{nicknames[writer]}: {message}\n"

            await brodcast_to_room(current_room, broadcast_message, writer) # calls 3rd function

            print(message)
            reply = "> "
            writer.write(reply.encode())
            await writer.drain()
    
    
    finally:
        await remove_client(writer) # calls 4th function
        
        writer.close()
        await writer.wait_closed()
        print(f"{username} Disconnected !")


async def start_server():
    print("Starting PySync Chat Server...")
    print("Preparing server configuration...")
    print(f"HOST : {HOST}")
    print(f"PORT : {PORT}")

    
    connection = connect_db()
    print("Database connected successfully !")

    server = await asyncio.start_server(
        lambda reader, writer : handle_client(reader, writer, connection),
        HOST,
        PORT
        )

    print("Server created Successfully !")

    async with server:
        await server.serve_forever()





if __name__ == '__main__':
    
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nDeveloper stopped the server using Ctrl + C.")