# PySync-Chat

PySync-Chat is a terminal-based asynchronous chat application built with Python. It supports multiple connected clients, public chat rooms, private messaging, authentication, message history, and a Textual-based Terminal User Interface (TUI).

The project started as a basic socket-based chat system and was developed into a multi-client chat application with persistent message storage and a dedicated TUI.

## Features

- User registration and login
- Password hashing and authentication
- Asynchronous TCP communication using `asyncio`
- Multiple simultaneous clients
- Public chat rooms
- Create and join rooms
- Leave rooms and return to `#general`
- Private DM conversations
- DM request system
- Accept and reject DM requests
- DM request notifications
- Multiple active DM conversations
- Switch between different rooms and DMs
- Persistent message history using SQLite
- Previous messages loaded when joining a room or DM
- `/where` command to display the current room or DM
- `/dmleave` command to leave an active DM
- Textual-based Terminal User Interface
- Scrollable room and DM lists
- Terminal resizing support
- Multi-client testing

## Tech Stack

- **Python**
- **asyncio**
- **TCP Sockets**
- **SQLite**
- **Textual**
- **Password Hashing**
- **CLI / TUI**

## Project Structure

```text
PySync-Chat/
│
├── client/
│   ├── client.py
│   ├── tui_client.py
│   └── ...
│
├── server/
│   ├── server.py
│   │
│   ├── handlers/
│   │   └── command_handler.py
│   │
│   └── services/
│       ├── auth_service.py
│       ├── database_service.py
│       ├── dm_service.py
│       ├── request_service.py
│       └── room_service.py
│
├── data/
│   └── ...
│
├── requirements.txt
└── README.md
```

The project is separated into client, server, command-handling, authentication, room, DM, request, and database components.

## Installation

Clone the repository:

```bash
git clone https://github.com/SachinK862007/PySync-Chat.git
cd PySync-Chat
```

Create a virtual environment:

### Windows

```bash
python -m venv .venv
```

Activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

Or in PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Running the Server

Start the server from the project root:

```bash
python -m server.server
```

The server uses the configured host and port and initializes the SQLite database connection.

## Running the TUI Client

Open another terminal and run:

```bash
python -m client.tui_client
```

The TUI provides the main interface for authentication, rooms, DMs, notifications, and messaging.

## Basic Usage

After starting the client:

1. Register a new account or log in.
2. Select a public room from the sidebar.
3. Send messages using the message input.
4. Switch between available rooms.
5. Send a DM request using:

```text
/dm <username>
```

6. View requests using:

```text
/requests
```

7. Accept or reject requests:

```text
/accept <username>
/reject <username>
```

8. Switch to an existing DM:

```text
/dm <username>
```

9. Leave the current DM:

```text
/dmleave
```

10. Check the current location:

```text
/where
```

11. Return to the general room:

```text
/leave
```

12. View available commands:

```text
/help
```

## Available Commands

```text
/help
/join <room>
/users
/rooms
/requests
/dm <username>
/accept <username>
/reject <username>
/leave
/dmleave
/where
/exit
```

## Message History

PySync-Chat stores chat messages using SQLite.

When a user joins a room or opens a DM, previously stored messages are loaded and displayed before new messages are received.

This allows conversations to continue across client sessions.

## Multi-Client Support

The server supports multiple clients simultaneously through Python's asynchronous networking model.

A typical test setup can use multiple terminals:

```text
Terminal 1 → Server
Terminal 2 → Client / User 1
Terminal 3 → Client / User 2
Terminal 4 → Client / User 3
Terminal 5 → Client / User 4
```

This can be used to test:

- Public room messaging
- Multiple users
- DM requests
- Accept/reject functionality
- DM isolation
- Switching between conversations
- Message history
- Notifications

## Screenshots

Screenshots of the application can be added here.

### Login Screen

Add a screenshot of the centered login/register screen:

```text
screenshots/login.png
```

### Main TUI

Add a screenshot showing:

- Room list
- DM list
- Message area
- Input area
- Notification section

```text
screenshots/main-tui.png
```

### DM Conversation

Add a screenshot showing a private conversation:

```text
screenshots/dm.png
```

### Notifications

Add a screenshot showing the DM request notification window:

```text
screenshots/notifications.png
```

You can create a `screenshots/` folder in the repository and place the images there.

## Testing

Before considering a build complete, test:

```text
Login
Registration
Invalid login
Duplicate registration
Multiple clients
Public room messaging
Room switching
Message history
DM requests
DM accept
DM reject
DM switching
DM message isolation
DM history
Notifications
/where
/leave
/dmleave
Terminal resizing
Client disconnect/reconnect
```

## Project Status

PySync-Chat is a completed Python chat application with asynchronous networking, authentication, public rooms, private messaging, persistent message history, and a Textual-based TUI.

## License

This project is available for learning and development purposes.