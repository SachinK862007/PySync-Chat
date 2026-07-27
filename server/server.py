import asyncio
from .config import HOST, PORT

async def handle_client(reader, writer):
    print("Client Connected !")
    try:
        while True:
            data = await reader.readline()
            if not data:
                break

            message = data.decode().strip()

            if message.upper() == 'EXIT':
                break

            print(message)
            reply = "hello client!\n"
            writer.write(reply.encode())
            await writer.drain()
    
    
    finally:
        writer.close()
        await writer.wait_closed()
        print("Client Disconnected !")


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