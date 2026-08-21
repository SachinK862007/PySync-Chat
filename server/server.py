from .handlers.command_handler import dispatch_command
from .services.database_service import connect_db
from .services.database_service import save_message
from .services.database_service import get_messages

import asyncio
import sqlite3
from .config import HOST, PORT

connected_clients = []
nicknames = {}
private_chats = {}
active_dms = {}
requests = []
rooms = {
    "general": []
}

commands = {
    "/join" : "Join a specific room. Usage :  /join <room_name>",
    "/dm" : "Send a private message. Usage : /dm <nickname> <message>",
    "/help" : "Display available commands. Usage : /help",
    "/rooms" : "Display available rooms. Usage : /rooms",
    "/users" : "Display users in the current room. Usage : /users",
    "/exit" : "Exit the chat. Usage : /exit"
}



#11th function to send the qury to the DB for public rooms
def execution(connection, sender, message, conversation):
    save_message(connection, nicknames[sender], message, conversation)

    #messages = get_messages(connection, conversation)
    #print(messages)
    

#11th function to send the qury to the DB for private messages
def execution_2(connection, sender, private_message, dm_id):
    save_message(connection, nicknames[sender], private_message, dm_id)

    #messages = get_messages(connection, dm_id)
    #print(messages)


#1st function 
async def find_current_room(writer):
    for room_name, clients in rooms.items():
        if writer in clients:
            return room_name

    return None



#2nd function
async def move_client(writer,room_name):
    current_room = await find_current_room(writer)

    rooms[current_room].remove(writer)
    rooms[room_name].append(writer)



#3rd function
async def brodcast_to_room(room_name, message, sender = None):
    for client in rooms[room_name]:
        if sender is None or client != sender:
            client.write(message.encode())
            await client.drain()



#4th function
async def remove_client(writer):
    current_room = await find_current_room(writer)
    if current_room is not None:
        rooms[current_room].remove(writer)

    if writer in connected_clients:
        connected_clients.remove(writer)
        nicknames.pop(writer,None)







#main function that call above functions
async def handle_client(reader, writer):


    connected_clients.append(writer)

    rooms["general"].append(writer)

    nickname_data = await reader.readline()
    
    nickname = nickname_data.decode().strip()
    
    nicknames[writer] = nickname
    
    print(f"{nickname} Connected to general room !")
    
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
                    requests
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
                
            current_room = await find_current_room(writer) #calls 1st function


            if message.upper() == "/HELP":

                reply = dispatch_command(
                    "/help",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests
                )

                writer.write(reply.encode())
                await writer.drain() 

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
                    requests
                )

                writer.write(reply.encode())
                await writer.drain() 

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
                    requests
                )

                writer.write(reply.encode())
                await writer.drain() 

                continue




            if message.upper() == "/LEAVE":

                reply = dispatch_command(
                    "/leave",
                    None,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests
                )

                writer.write(f"{reply}\n".encode())
                await writer.drain()

                continue





            if message.upper() == "/DM" or message.upper().startswith("/DM "):

                parts = message.split(maxsplit=2)
            
                if len(parts) < 2:
                    reply = "Usage: /dm <nickname>\n"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue
            
                target_nickname = parts[1]
            
                target_writer = None
            
                for client, nickname in nicknames.items():
                
                    if nickname.lower() == target_nickname.lower():
                        target_writer = client
                        break
            
                if target_writer is None:
                    reply = f"User {target_nickname} not found!\n"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue
            
                reply = dispatch_command(
                    "/dm",
                    target_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests
                )
            
                writer.write(f"{reply}\n".encode())
                await writer.drain()
            
                continue
            



            if message.upper() == "/ACCEPT" or message.upper().startswith("/ACCEPT "):

                parts = message.split(maxsplit = 1)

                if len(parts) < 2:
                    reply = "Usage: /accept <nick_name>"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue

                sender_nickname = parts[1]

                reply = dispatch_command(
                    "/accept",
                    sender_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests
                )

                writer.write(f"{reply}\n".encode())
                await writer.drain()

                continue




            if message.upper() == "/REJECT" or message.upper().startswith("/REJECT "):

                parts = message.split(maxsplit = 1)

                if len(parts) < 2:
                    reply = "Usage: /reject <nick_name>"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue

                sender_nickname = parts[1]

                reply = dispatch_command(
                    "/reject",
                    sender_nickname,
                    writer,
                    nicknames[writer],
                    nicknames,
                    rooms,
                    private_chats,
                    requests
                )

                writer.write(f"{reply}\n".encode())
                await writer.drain()

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
                    requests
                )

                if reply == "exit":
                    break

                writer.write(f"{reply}\n".encode())
                await writer.drain()

                continue



            execution(connect_db(), writer, message, current_room) # calls 11th function public messages

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
        print(f"{nickname} Disconnected !")


async def start_server():
    print("Starting PySync Chat Server...")
    print("Preparing server configuration...")
    print(f"HOST : {HOST}")
    print(f"PORT : {PORT}")

    
    connection = connect_db()
    print("Database connected successfully !")

    server = await asyncio.start_server(handle_client, HOST, PORT)

    print("Server created Successfully !")

    async with server:
        await server.serve_forever()





if __name__ == '__main__':
    
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nDeveloper stopped the server using Ctrl + C.")