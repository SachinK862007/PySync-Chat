async def find_current_room(writer, rooms):
    for room_name, clients in rooms.items():
        if writer in clients:
            return room_name

    return None




def create_room(room_name, rooms):
    
    if room_name in rooms:
        return False
    
    rooms[room_name] = []

    return True


def leave_room(writer, rooms):
    for room_name, clients in rooms.items():
        if writer in clients:

            clients.remove(writer)

            if room_name != "general":
                rooms["general"].append(writer)

            return room_name

    return None



def join_room(writer, room_name, rooms):
    current_room = find_user_room(writer, rooms)
    
    if current_room == room_name:
        return False

    if current_room:
        rooms[current_room].remove(writer)

    create_room(room_name, rooms)

    rooms[room_name].append(writer)

    return True


def find_user_room(writer, rooms):

    for room_name, clients in rooms.items():
        if writer in clients:
            return room_name

    return None



if __name__ == "__main__":
    user_1 = "user_1"
    user_2 = "user_2"

    rooms = {
        "general": [user_1],
        "python": [user_2]
    }

    print(find_user_room(user_1, rooms))

    print(join_room(user_1, "python", rooms))
    print(rooms)

    left_room = leave_room(user_1, rooms)

    print("Left:", left_room)
    print(rooms)

    print("Left again:", leave_room(user_1, rooms))

    print("Create gaming:", create_room("gaming", rooms))
    print("Create gaming again:", create_room("gaming", rooms))
    
    print(rooms)