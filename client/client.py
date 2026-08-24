#from .services.database_service import connect_db
#from .services.database_service import save_message
#from .services.database_service import get_messages
#from .services.auth_service import login_user
#from .services.auth_service import register_user

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






async def authenticate_client(reader, writer):

    #await send_reply(writer, "Welcome to PySync Chat!")

    data = await reader.readline()

    if not data:
        return False

    print(data.decode().strip())

    while True:

        data = await reader.readline()

        if not data:
            return False

        print(data.decode().strip())


        data = await reader.readline()

        if not data:
            return False

        print(data.decode().strip())


        choice = await asyncio.to_thread(input, "> ")

        writer.write((choice + "\n").encode())
        await writer.drain()

        if choice.strip() == "":
            
            data  = await reader.readline()

            if not data:
                return False

            print(data.decode().strip())

            username = await asyncio.to_thread(input, "> ")

            writer.write((username + "\n").encode())
            await writer.drain()

            data = await reader.readline()

            if not data:
                return False

            print(data.decode().strip())

            password = await asyncio.to_thread(input, "> ")

            writer.write((password + "\n").encode())
            await writer.drain()

            data = await reader.readline()

            if not data:
                return False

            result = data.decode().strip()
            print(result)

            if result == "Login successful!":
                return True

            continue

        elif choice.upper() == "R":
            data = await reader.readline()

            if not data:
                return False

            print(data.decode().strip())  

            
            username = await asyncio.to_thread(input, "> ")

            writer.write((username + "\n").encode())
            await writer.drain()

            data = await reader.readline()

            if not data:
                return False

            print(data.decode().strip())

            
            username = await asyncio.to_thread(input, "> ")

            writer.write((password + "\n").encode())
            await writer.drain()

            data = await reader.readline()

            if not data:
                return False

            result = data.decode().strip()

            print(result)

            if result == "Registration Successful !":
                return True 

            continue



async def start_client():

    reader, writer = await asyncio.open_connection(HOST, PORT)


    authenticated = await authenticate_client(reader, writer)


    if not authenticated:

        writer.close()
        await writer.wait_closed()

        return


    print("\nConnected successfully. You can start chatting.\n")


    await asyncio.gather(send_messages(writer), receive_messages(reader))


if __name__ == "__main__":

    try:

        asyncio.run(start_client())

    except KeyboardInterrupt:

        print("\nDeveloper stopped the connection using Ctrl + C.")