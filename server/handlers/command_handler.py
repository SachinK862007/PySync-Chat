def handle_help():
    
    return """
    Available commands :

    /help
    /join <room>
    /users
    /rooms
    /dm <username>
    /accept <username>
    /reject <username>
    /leave
    /exit
    """


if __name__ == '__main__':
    print(handle_help())