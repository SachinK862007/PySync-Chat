import asyncio
import sqlite3
from .config import HOST, PORT

connected_clients = []
nicknames = {}
private_chats = {}
active_dms = {}
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

#storage for chat history "connection"
def connect_db():
    connection = sqlite3.connect("pysync_chat.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            message TEXT,
            conversation TEXT,
            timestamp TEXT
        )
    """)

    connection.commit()
    return connection



#function to save the chat in the DB
def save_message(connection, sender, message, conversation):
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (sender, message, conversation, timestamp)
        VALUES (?, ?, ?, datetime('now'))
    """, (sender, message, conversation))

    connection.commit()

#function to retrieve the chat history from the DB
def get_messages(connection, conversation):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM messages WHERE conversation = ? ORDER BY id ASC", (conversation,))
    messages = cursor.fetchall()
    return messages


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
    for writer, nickname in nicknames.items():
        if nickname.upper() == target_nickname.upper():
            return writer

    return None



#9th function
async def find_private_chat(writer, target_writer):
    for dm_id, members in private_chats.items():
        if writer in members and target_writer in members:
         return dm_id

    return None




#10th function
async def create_private_chat(writer, target_writer):
    existing_dm = await find_private_chat(writer, target_writer)
    if existing_dm is not None:
        return existing_dm

    dm_id = f"dm_{len(private_chats) + 1}"
    private_chats[dm_id] = [writer, target_writer]
    return dm_id



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
                    reply = f"You are already in {room_name} room !\n"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue

                if room_name not in rooms:
                    rooms[room_name] = []

                await move_client(writer,room_name)    # calls 2nd function
                
                history = get_messages(connect_db(), room_name)
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
                await handle_help(writer) # calls 5th function
                continue

            if message.upper() == "/ROOMS":
                await handle_rooms(writer) # calls 6th function
                continue

            if message.upper() == "/USERS":
                await handle_users(writer) # calls 7th function
                continue

            if message.upper() == "/DM" or message.upper().startswith("/DM "):
                parts = message.split(maxsplit = 2)
                if len(parts) < 3:
                    reply = "Usage: /dm <nickname> <message>\n"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue

                target_nickname = parts[1]
                private_message = parts[2]

                target_writer = await find_user_by_nickname(target_nickname) # calls 8th function

                if target_writer is None:
                    reply = f"User {target_nickname} not found !\n"
                    writer.write(reply.encode())
                    await writer.drain()
                    continue

                dm_id = await create_private_chat(writer, target_writer) # calls 10th function
                dm_message = f"[DM from {nicknames[writer]}] : {private_message}\n"

                execution_2(connect_db(), writer, private_message, dm_id) # calls 11th function private messages
                target_writer.write(dm_message.encode())
                await target_writer.drain()
                continue


            if message.upper() == '/EXIT':
                break

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