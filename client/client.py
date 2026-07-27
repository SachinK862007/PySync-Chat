import asyncio
from server.config import HOST, PORT

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    while True:
        message = input("> ") + "\n"
        writer.write(message.encode())
        await writer.drain()
        data = await reader.readline()
        reply = data.decode()
        print(reply)



if __name__ == '__main__':
    asyncio.run(start_client())



"""
 if message.upper() == 'EXIT':
            while True:
                enter = input("\nDo u confirm to EXIT ? (YES) or (NO) : ")
                if enter.upper() == 'YES':
                    return 'EXIT'
                elif enter.upper() == 'NO':
                    break
                else:
                    print("\nInvalid Input")    
            
"""