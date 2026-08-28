import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    OptionList,
    RichLog,
    Static,
)
from textual.widgets.option_list import Option
from server.config import HOST, PORT


class ServerConnection:

    def __init__(self):

        self.reader = None
        self.writer = None

        self.incoming = asyncio.Queue()
        self.reader_task = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(HOST, PORT)

        self.reader_task = asyncio.create_task(self.read_loop())

    async def read_loop(self):

        try:

            while True:

                data = await self.reader.readline()

                if not data:
                    await self.incoming.put("__CONNECTION_CLOSED__")
                    break

                message = data.decode(errors="replace").rstrip("\r\n")

                await self.incoming.put(message)

        except asyncio.CancelledError:
            raise

        except Exception as error:

            await self.incoming.put(
                f"__CONNECTION_ERROR__:{error}"
            )


    async def send(self, message):
        if self.writer is None:
            return

        self.writer.write(f"{message}\n".encode())
        await self.writer.drain()


    async def receive(self):
        return await self.incoming.get()

    def close(self):

        if self.writer is not None:
            self.writer.close()

    async def wait_closed(self):
        if self.writer is not None:
            await self.writer.wait_closed()



class RequestScreen(ModalScreen):

    def __init__(self, app):
        super().__init__()

        self.chat_app = app

    def compose(self) -> ComposeResult:

        with Container(id = "request_box"):

            yield Static("DM Requests", id = "request_title")

            yield OptionList(id = "request_list")


            with Horizontal(id = "request_buttons"):

                yield Button("Accept", id = "request_accept")

                yield Button("Reject", id = "request_reject")
                
                yield Button("Back", id = "request_back")


    def on_mount(self):

        self.refresh_requests()


    def refresh_requests(self):

        request_list = self.query_one("#request_list", OptionList)

        request_list.clear_options()

        for username in self.chat_app.pending_requests:

            request_list.add_option(Option(username, id = username))


    def selected_request(self):

        request_list = self.query_one("#request_list", OptionList)

        if request_list.highlighted_option is None:
            return None

        return request_list.highlighted_option.id


    async def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "request_back":
            self.app.pop_screen()
            return

        username = self.selected_request()

        if username is None:

            self.chat_app.set_status("Select a DM request first.")
            return

        if event.button.id == "request_accept":

            await self.chat_app.send_command(f"/accept {username}")

            if username in self.chat_app.pending_requests:
                self.chat_app.pending_requests.remove(username)

            self.refresh_requests()
            await self.chat_app.refresh_dms()
            return

        if event.button.id == "request_reject":

            await self.chat_app.send_command(f"/reject {username}")

            if username in self.chat_app.pending_requests:

                self.chat_app.pending_requests.remove(username)

            self.refresh_requests()


class PySyncTUI(App):
    
    TITLE = "PySync Chat"

    CSS = """
    Screen {
        layout: vertical;
    }

    #auth_area {
        width: 1fr;
        height: 1fr;
        align: center middle;
    }

    #auth_panel {
        width: 60%;
        min-width: 50;
        max-width: 90;
        height: auto;
        padding: 2;
        border: solid $primary;
    }

    #auth_title {
        text-align: center;
        width: 100%;
        margin-bottom: 2;
    }

    #auth_status {
        width: 100%;
        height: auto;
        margin-top: 1;
    }

    #main_panel {
        width: 1fr;
        height: 1fr;
    }

    #sidebar {
        width: 30%;
        min-width: 24;
        max-width: 40;
        height: 1fr;
        padding: 1;
        border-right: solid $panel;
    }

    #sidebar_scroll {
        width: 1fr;
        height: 1fr;
        overflow-y: hidden;
        align: left top;
    }

    .section_title {
        width: 100%;
        margin-top: 1;
        margin-bottom: 1;
    }

    #rooms_list {
        height: 1fr;
        min-height: 4;
        max-height: 12;
    }

    #dm_list {
        height: 1fr;
        min-height: 4;
        max-height: 16;
    }

    #notifications {
        width: 100%;
        height: auto;
        dock: bottom;
    }

    #notification_summary {
        width: 100%;
        height: 2;
        padding: 0 1;
    }

    #chat_area {
        width: 1fr;
        height: 1fr;
    }

    #context_label {
        width: 100%;
        height: 3;
        padding: 1;
        content-align: left middle;
        background: $surface;
        border-bottom: solid $panel;
    }

    #message_log {
        width: 1fr;
        height: 1fr;
    }

    #message_input {
        width: 1fr;
        height: 3;
    }

    #request_box {
        width: 65%;
        min-width: 50;
        max-width: 80;
        height: 60%;
        min-height: 16;
        padding: 2;
        background: $panel;
        border: solid $primary;
        align: center middle;
    }

    #request_title {
        width: 100%;
        height: 3;
        text-align: center;
    }

    #request_list {
        width: 1fr;
        height: 1fr;
    }

    #request_buttons {
        width: 100%;
        height: 3;
    }

    #request_buttons Button {
        width: 1fr;
    }

    .hidden {
        display: none;
    }
    """

    def __init__(self):

        super().__init__()

        self.connection = ServerConnection()

        self.username = None

        self.auth_ready = False

        self.auth_in_progress = None

        self.current_context = None

        self.current_context_name = None

        self.rooms = []

        self.dms = []

        self.pending_requests = set()

        self.server_task = None

        self.context_switch_lock = asyncio.Lock()
        self.context_history_ready = asyncio.Event()


    def compose(self) -> ComposeResult:

        yield Header()

        with Container(id="auth_area"):
            with Container(id="auth_panel"):

                yield Static("PySync Chat", id="auth_title")

                yield Input(placeholder="Username", id="auth_username")

                yield Input(placeholder="Password", password=True, id="auth_password")

                with Horizontal():
                    yield Button("Login", id="login_button")

                    yield Button("Register", id="register_button")

                yield Static("Connecting...", id="auth_status")

        with Horizontal(id = "main_panel", classes = "hidden"):

            with Vertical(id = "sidebar"):

                with Vertical(id = "sidebar_scroll"):
                    yield Static("ROOMS", classes="section_title")

                    yield OptionList(id="rooms_list")

                    yield Static("DMs", classes="section_title")

                    yield OptionList(id="dm_list")

                yield Static("Notifications: 0", id="notification_summary")
                yield Button("Notifications", id="notifications")


            with Vertical(id="chat_area"):

                yield Static("Current conversation: Not connected", id="context_label")

                yield RichLog(id="message_log",wrap=True, markup=False, auto_scroll=True)

                yield Input(placeholder="Type a message or /command", id="message_input")


        yield Footer()

    
    async def on_mount(self):

        try:

            await self.connection.connect()

            #self.server_task = asyncio.create_task(self.process_server_messages())

            await self.consume_initial_auth_messages()

            self.auth_ready = True

            self.set_status("Ready. Choose Login or Register.")

        except Exception as error:

            self.set_status(f"Connection failed: {error}")


    async def consume_initial_auth_messages(self):

        welcome = await self.connection.receive()
        if welcome.startswith("__CONNECTION_"):
            raise ConnectionError(welcome)

        first_prompt = await self.connection.receive()
        second_prompt = await self.connection.receive()

        if "Login" not in first_prompt or "Register" not in second_prompt:
            raise ConnectionError("Unexpected authentication menu from server")


    def set_status(self, message):

        self.query_one("#auth_status", Static).update(message)

        try:

            self.query_one("#status_text", Static).update(message)

        except Exception:

            pass


    async def perform_auth(self, mode):

        if not self.auth_ready:
            return

        if self.auth_in_progress:
            return            

        self.auth_in_progress = True

        username = self.query_one("#auth_username", Input).value.strip()

        password = self.query_one("#auth_password", Input).value

        if not username or not password:

            self.set_status("Username and password are required.")

            self.auth_in_progress = False

            return


        try:

            if mode == "login":

                await self.connection.send("")

            else:

                await self.connection.send("R")

            response = await self.connection.receive()
            if response.startswith("__CONNECTION_") or "username" not in response.lower():
                self.set_status(response)
                return

            await self.connection.send(username)

            response = await self.connection.receive()
            if response.startswith("__CONNECTION_") or "password" not in response.lower():
                self.set_status(response)
                return

            await self.connection.send(password)

            result = await self.connection.receive()
            result = result.strip()
            self.set_status(result)


            if (
                result == "Login successful!"
                or result == "Registration Successful !"
                or result == "Registration Successful !\n"
            ):

                self.username = username

                self.query_one("#auth_area").add_class("hidden")

                self.query_one("#main_panel").remove_class("hidden")

                self.query_one("#context_label", Static).update(
                    "Current conversation: #general"
                )

                self.current_context = "room"

                self.current_context_name = "general"

                self.set_status("Connected successfully.")

                if self.server_task is None:

                    self.server_task = asyncio.create_task(self.process_server_messages())

                await self.refresh_rooms()

                await self.refresh_dms()

                await self.select_room("general")

                return

            await self.consume_auth_menu()


        except Exception as error:

            self.set_status(f"Authentication error: {error}")

        finally:

            self.auth_in_progress = False

    async def consume_auth_menu(self):
        first_prompt = await self.connection.receive()
        second_prompt = await self.connection.receive()

        if "Login" not in first_prompt or "Register" not in second_prompt:
            raise ConnectionError("Unexpected authentication menu from server")


    async def on_button_pressed(self, event: Button.Pressed):

        if event.button.id == "login_button":

            await self.perform_auth("login")

        elif event.button.id == "register_button":

            await self.perform_auth("register")

        elif event.button.id == "notifications":

            self.push_screen(RequestScreen(self))


    async def send_command(self, command):

        await self.connection.send(command)


    async def on_input_submitted(self, event: Input.Submitted):

        if event.input.id != "message_input":
            return

        message = event.value.strip()

        event.input.value = ""

        if not message:
            return


        if message.startswith("/"):
            command, _, argument = message.partition(" ")

            if command.lower() == "/join" and argument.strip():
                room_name = argument.strip()
                await self.select_room(room_name)
                await self.refresh_rooms()
                return

            if command.lower() == "/dm" and argument.strip():
                target_username = argument.strip()
                for username in self.dms:
                    if username.lower() == target_username.lower():
                        await self.select_dm(username)
                        return

            await self.send_command(message)

            return


        # Normal message
        await self.send_command(message)
        self.add_message(f"{self.username}: {message}")


    async def refresh_rooms(self):

        self.rooms = []

        await self.send_command("/tui_rooms")


    async def refresh_dms(self):

        self.dms = []

        await self.send_command("/tui_dms")


    async def select_room(self, room_name):

        async with self.context_switch_lock:
            self.context_history_ready.clear()
            self.current_context = "room"
            self.current_context_name = room_name
            self.clear_messages()
            await self.send_command(f"/tui_room {room_name}")
            try:
                await asyncio.wait_for(self.context_history_ready.wait(), timeout=10)
            except asyncio.TimeoutError:
                self.add_message("Timed out loading room history.")


    async def select_dm(self, username):

        async with self.context_switch_lock:
            self.context_history_ready.clear()
            self.current_context = "dm"
            self.current_context_name = username
            self.clear_messages()
            await self.send_command(f"/tui_dm {username}")
            try:
                await asyncio.wait_for(self.context_history_ready.wait(), timeout=10)
            except asyncio.TimeoutError:
                self.add_message("Timed out loading DM history.")


    def clear_messages(self):

        self.query_one("#message_log", RichLog).clear()


    def add_message(self, message):

        self.query_one("#message_log", RichLog).write(message)


    async def process_server_messages(self):

        while True:

            message = await self.connection.receive()

            if message == "__CONNECTION_CLOSED__":

                self.add_message("Connection closed by server.")

                break


            if message.startswith("__CONNECTION_ERROR__:"):

                self.add_message(message)

                break


            await self.handle_server_message(message)


    async def handle_server_message(self, message):

        if message.startswith("__TUI_ROOM_ADDED__:"):
            room_name = message[len("__TUI_ROOM_ADDED__:"):].strip()
            if room_name and room_name not in self.rooms:
                self.rooms.append(room_name)
                self.update_room_list()
            return

        if message.startswith("__TUI_DM_ADDED__:"):
            username = message[len("__TUI_DM_ADDED__:"):].strip()
            if username and username not in self.dms:
                self.dms.append(username)
                self.update_dm_list()
            return

        if message == "__TUI_ROOMS_BEGIN__":

            self.rooms = []

            return


        if message == "__TUI_ROOMS_END__":

            self.update_room_list()

            return


        if message.startswith("ROOM:"):

            room_name = message[len("ROOM:")::]

            if room_name not in self.rooms:

                self.rooms.append(room_name)

            return


        if message == "__TUI_DMS_BEGIN__":

            self.dms = []

            return


        if message == "__TUI_DMS_END__":

            self.update_dm_list()

            return


        if message.startswith("DM:"):

            username = message[len("DM:")::].strip()

            if username not in self.dms:

                self.dms.append(username)

            return


        if message.startswith("__TUI_CONTEXT__:ROOM:"):

            room_name = message.split(":", 2)[2]

            self.current_context = "room"
            self.current_context_name = room_name

            self.query_one("#context_label", Static).update(
                f"Current conversation: #{room_name}"
            )

            return


        if message.startswith("__TUI_CONTEXT__:DM:"):

            username = message.split(":", 2)[2]

            self.current_context = "dm"
            self.current_context_name = username

            self.query_one("#context_label", Static).update(
                f"Current conversation: DM: {self.username} <-> {username}"
            )

            return


        if message.startswith("__TUI_HISTORY__:"):

            history_message = message[len("__TUI_HISTORY__:")::]

            self.add_message(history_message)

            return


        if message == "__TUI_HISTORY_END__":
            self.context_history_ready.set()
            return


        if message.startswith("__TUI_ERROR__:"):

            self.add_message(message[len("__TUI_ERROR__:")::])
            self.context_history_ready.set()

            return


        if "sent to a DM request" in message or "sent you a DM request" in message:
            marker = "sent to a DM request" if "sent to a DM request" in message else "sent you a DM request"
            sender = message.split(marker, 1)[0].strip()

            self.pending_requests.add(sender)

            self.refresh_notification_button()

            self.add_message(f"DM request from {sender}")

            if self.screen.__class__ == RequestScreen:
                self.screen.refresh_requests()

            return


        if ("accepted your DM request" in message):

            parts = message.split(" accepted your DM request", 1)

            if parts:

                username = parts[0].strip()

                if username not in self.dms:

                    self.dms.append(username)

                    self.update_dm_list()

            self.add_message(message)

            return


        if message.startswith("[DM] "):

            dm_message = message[len("[DM] "):]

            sender = dm_message.split(":", 1)[0].strip()


            # Show the message only if this DM is open
            if (
                self.current_context == "dm"
                and self.current_context_name
                and sender.lower()
                == self.current_context_name.lower()
            ):

                self.add_message(message)

            else:

                if sender not in self.dms:

                    self.dms.append(sender)

                    self.update_dm_list()

                self.add_message(f"New DM from {sender}")

            return


        # Request status response
        if (message.startswith("- from ") and ": pending" in message):

            sender = message[len("- from "):].split(":", 1)[0].strip()

            self.pending_requests.add(sender)

            self.refresh_notification_button()

            if self.screen.__class__ == RequestScreen:

                self.screen.refresh_requests()

            return

        if message.startswith("-from ") and ": pending" in message:
            sender = message[len("-from "):].split(":", 1)[0].strip()
            self.pending_requests.add(sender)
            self.refresh_notification_button()
            if self.screen.__class__ == RequestScreen:
                self.screen.refresh_requests()
            return


        # Normal server response / public message
        if message == ">":
            return

        if self.current_context == "room":

            self.add_message(message)

        elif (
            self.current_context == "dm"
            and (
                message.startswith("DM request")
                or message.startswith("Switched to DM")
                or message.startswith("You ")
            )
        ):

            self.add_message(message)


    def update_room_list(self):

        room_list = self.query_one("#rooms_list", OptionList)

        room_list.clear_options()

        for room_name in self.rooms:

            room_list.add_option(Option(f"# {room_name}", id=f"room:{room_name}"))


    def update_dm_list(self):

        dm_list = self.query_one("#dm_list", OptionList)

        dm_list.clear_options()

        for username in self.dms:

            dm_list.add_option(Option(username, id=f"dm:{username}"))


    def refresh_notification_button(self):

        button = self.query_one("#notifications", Button)

        count = len(self.pending_requests)

        self.query_one("#notification_summary", Static).update(
            f"Notifications: {count}"
        )

        if count:

            button.label = (
                f"Notifications "
                f"({count})"
            )

        else:

            button.label = ("Notifications")


    def on_option_list_option_selected(self, event: OptionList.OptionSelected):

        option_id = event.option_id

        if option_id is None:
            return


        if option_id.startswith("room:"):

            room_name = option_id[len("room:")::]

            asyncio.create_task(self.select_room(room_name))

            return


        if option_id.startswith("dm:"):

            username = option_id[len("dm:")::]

            asyncio.create_task(self.select_dm(username))

    async def on_unmount(self):
        if self.server_task is not None:
            self.server_task.cancel()
        self.connection.close()
        await self.connection.wait_closed()


if __name__ == "__main__":

    PySyncTUI().run()
