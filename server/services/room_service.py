def join_room(writer, room_name, rooms):
    current_room = find_user_room(writer, rooms)
    
    if current_room == room_name:
        return False

    if current_room:
        rooms[current_room].remove(writer)

    if room_name not in rooms:
        rooms[room_name] = []

    rooms[room_name].append(writer)

    return True


def find_user_room(writer, rooms):

    for room_name, clients in rooms.items():
        if writer in clients:
            return room_name

    return None



if __name__ == '__main__':
    user_1 = "user_1"
    user_2 = "user_2"

    rooms = {
        "general" : [user_1],
        "python" : [user_2]
    }

    print(find_user_room(user_1, rooms))
    print(find_user_room(user_2, rooms))
    print(find_user_room("user_3", rooms))

    print(join_room(user_1, "python", rooms))
    print(rooms)

    print(join_room(user_1, "gaming", rooms))
    print(rooms)
    
    print(join_room(user_1, "gaming", rooms))
    print(rooms)