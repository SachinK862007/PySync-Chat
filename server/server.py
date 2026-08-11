import asyncio
from .config import HOST, PORT

connected_clients = []
nicknames = {}
private_chats = {}
rooms = {
    "general": []
}

commands = {
    "/join" : "Join a specific room. Usage :  /join <room_name>",
    "/help" : "Display available commands. Usage : /help",
    "/rooms" : "Display available rooms. Usage : /rooms",
    "/users" : "Display users in the current room. Usage : /users",
    "/exit" : "Exit the chat. Usage : /exit"
}


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



#5th function 
async def handle_help(writer):
    help_message = "Available Commands\n"
    
    for command, description in commands.items():
        help_message += f"{command} : {description}\n"
    
    writer.write(help_message.encode())
    await writer.drain()



#6th function
async def handle_rooms(writer):
    rooms_message = "Available Rooms\n"
    
    for room_name in rooms:
        rooms_message += f"{room_name}\n"

    writer.write(rooms_message.encode())
    await writer.drain()



#7th function
async def handle_users(writer):
    current_room = await find_current_room(writer)
    users_message = f"Users in {current_room}\n"

    for client in rooms[current_room]:
        users_message += f"{nicknames[client]}\n"

    writer.write(users_message.encode())
    await writer.drain()



#8th function
async def find_user_by_nickname(target_nickname):
    for writer, nickname in nicknames.item():
        if nickname.upper() == target_nickname.upper():
            return writer

    return None



#9th function
async def create_private_chat(writer, target_nickname):
    pass




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

                current_room = await find_current_room(writer) #calls 1st function

                if current_room == room_name:
                    replay = f"You are already in {room_name} room !\n"
                    writer.write(replay.encode())
                    await writer.drain()
                    continue

                if room_name not in rooms:
                    rooms[room_name] = []

                await move_client(writer,room_name)    # calls 2nd function
                
                join_message = f"{nicknames[writer]} joined : {room_name}\n"

                await brodcast_to_room(room_name, join_message) # calls 3rd function

                
            current_room = await find_current_room(writer) #calls 1st function


            if message.upper() == "/HELP":
                await handle_help(writer) # calls 5th function
                continue

            if message.upper() == "/ROOMS":
                await handle_rooms(writer) # calls 6th function
                continue

            if message.upper() == "/USERS":
                await handle_users(writer) # calls 7th function
                continue

            if message.upper() == '/EXIT':
                break

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

    server = await asyncio.start_server(handle_client, HOST, PORT)

    print("Server created Successfully !")

    async with server:
        await server.serve_forever()
    


if __name__ == '__main__':
    
    try:
        asyncio.run(start_server())
    except KeyboardInterrupt:
        print("\nDeveloper stopped the server using Ctrl + C.")