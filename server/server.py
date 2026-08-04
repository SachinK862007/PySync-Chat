import asyncio
from .config import HOST, PORT

connected_clients = []
nicknames = {}
rooms = {
    "general": []
}
#client_rooms = {}

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

                if room_name not in rooms:
                    rooms[room_name] = []
                    rooms["general"].remove(writer)
                    rooms[room_name].append(writer)
                    join_message = f"{nicknames[writer]} joined : {room_name}\n"

                    for client in rooms[room_name]:
                        client.write(join_message.encode())
                        await client.drain()

                room_name = message.split(maxsplit = 1)[1]

            for room_name, clients in rooms.items():
                if writer in clients:
                    current_room = room_name
                    break


            if message.upper() == 'EXIT':
                break

            broadcast_message = f"{nicknames[writer]}: {message}\n"

            for client in rooms[current_room]:
                if client != writer:
                    client.write(broadcast_message.encode())
                    await client.drain()

            print(message)
            reply = "> "
            writer.write(reply.encode())
            await writer.drain()
    
    
    finally:
        try:

            connected_clients.remove(writer)
            nicknames.pop(writer, None)
            rooms["general"].remove(writer)
        
        except ValueError:
            pass

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