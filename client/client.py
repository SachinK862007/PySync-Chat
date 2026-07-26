import asyncio
from server.config import HOST, PORT

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    message = "hello Server!\n"
    writer.write(message.encode())
    await writer.drain()
    data = await reader.readline()
    reply = data.decode()
    print(reply)



if __name__ == '__main__':
    asyncio.run(start_client())