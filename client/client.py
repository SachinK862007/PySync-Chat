import asyncio
from server.config import HOST, PORT

async def send_messages(writer):
    while True:
        message = await asyncio.to_thread(input, "> ")
        message += "\n"
        
        if message.upper().strip() == 'EXIT':
            while True:
                enter = await asyncio.to_thread(input,"\nDo u confirm to EXIT ? (YES) or (NO) : ")
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


async def receive_messages(reader):
    while True:

        data = await reader.readline()

        if not data:
            break

        reply = data.decode()
        print(reply)



async def start_client():

    name = input("Enter your nickname : ")

    reader, writer = await asyncio.open_connection(HOST, PORT)

    writer.write((name + "\n").encode())
    await writer.drain()

    await asyncio.gather(send_messages(writer), receive_messages(reader))



if __name__ == '__main__':
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("\nDeveloper stopped the connectionusing Ctrl + C.")

