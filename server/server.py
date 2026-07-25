import asyncio
from config import HOST, PORT

async def handle_client(reader, writer):
    pass



async def start_server():
    print("Starting PySync Chat Server...")
    print("Preparing server configuration...")
    print(f"HOST : {HOST}")
    print(f"PORT : {PORT}")

    server = await asyncio.start_server(handle_client, HOST, PORT)

    print("Server created Successfully !")
    


if __name__ == '__main__':
    asyncio.run(start_server())