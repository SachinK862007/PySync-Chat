import asyncio
from server.config import HOST, PORT

async def start_client():
    reader, writer = await asyncio.open_connection(HOST, PORT)
    while True:
        message = input("> ") + "\n"
        
        if message.upper().strip() == 'EXIT':
            while True:
                enter = input("\nDo u confirm to EXIT ? (YES) or (NO) : ")
                if enter.upper() == 'YES':
                    message = "EXIT\n"
                    break
                elif enter.upper() == 'NO':
                    break
                else:
                    print("\nInvalid Input") 

            if enter.upper() == 'NO':
                continue

        writer.write(message.encode())
        await writer.drain()
        if message.strip().upper() == 'EXIT':
            break
        data = await reader.readline()
        reply = data.decode()
        print(reply)



if __name__ == '__main__':
    asyncio.run(start_client())


