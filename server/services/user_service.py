def remove_user(nickname, users):

    username = find_user_by_nickname(nickname, users)

    if username is None:
        return False

    del users[username]
    return True 


def add_user(nickname, users):

    if find_user_by_nickname(nickname, users):
        return False

    users[nickname] = True
    return True


def find_user_by_nickname(nickname, users):

    for username in users:
        if username.lower() == nickname.lower():
            return username

    return None





if __name__ == "__main__":
    users = {
        "Alice": True,
        "Sachin": True,
        "John": True
    }

    print(find_user_by_nickname("alice", users))

    print(add_user("Rahul", users))
    print(users)

    print(remove_user("rahul", users))
    print(users)

    print(remove_user("Rahul", users))
    print(users)