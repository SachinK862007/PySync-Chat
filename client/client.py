import asyncio
from server.config import HOST, PORT

async def send_messages(writer):
    while True:
        message = await asyncio.to_thread(input, "> ")
        message += "\n"
        
        if message.upper().strip() == '/EXIT':
            while True:
                enter = await asyncio.to_thread(input,"\nDo u confirm to EXIT ? (YES) or (NO) : ")
                if enter.upper() == 'YES':
                    message = "/EXIT\n"
                    break
                elif enter.upper() == 'NO':
                    break
                else:
                    print("\nInvalid Input") 

            if enter.upper() == 'NO':
                continue

        writer.write(message.encode())
        await writer.drain()
        if message.strip().upper() == '/EXIT':
            break


async def receive_messages(reader):
    while True:

        data = await reader.readline()

        if not data:
            break

        reply = data.decode()
        print(reply)



async def start_client():

    reader, writer = await asyncio.open_connection(HOST, PORT)

    while True:
        message = await reader.readline()

        if not message:
            break

        print(message.decode().strip())

        if "Press ENTER to Login" in message.decode():
            choice = await asyncio.to_thread(input, "> ")
            writer.write((choice + "\n").encode())
            await writer.drain()

        elif "Type R to Register" in message.decode():
            continue

        elif "Username : " in message.decode() or "Choose username : " in message.decode():
            username = await asyncio.to_thread(input, "> ")
            writer.write((username + "\n").encode())
            await writer.drain()

        elif "Password : " in message.decode() or "Choose password : " in message.decode():
            password = await asyncio.to_thread(input, "> ")
            writer.write((password + "\n").encode())
            await writer.drain()

        elif "Login successful !" in message.decode() or "Registration Successful !" in message.decode():
            break

    await asyncio.gather(send_messages(writer), receive_messages(reader))



if __name__ == '__main__':
    try:
        asyncio.run(start_client())
    except KeyboardInterrupt:
        print("\nDeveloper stopped the connectionusing Ctrl + C.")

