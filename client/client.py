import asyncio
from server.config import HOST, PORT

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)



if __name__ == '__main__':
    asyncio.run(start_client())