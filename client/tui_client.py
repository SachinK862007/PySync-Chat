import asyncio

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll, Container
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
        self.reader, self.writer = await asyncio.open_connection(HOST, POST)

        self.reader_task = asyncio.create_task(self.read_loop())

    async def read_loop(self):

        try:

            with True:

                data = await self.reader.readline()

                if not data:
                    await self.incoming.put("__CONNECTION_CLOSED__")
                    break

                message = (data.decode(errors = "replace").rstrip("\n"))

                await self.incoming.put(message)

        except asyncio.CancelledError:
            raise

        except Exception as error:

            await self.incoming.put(f"__COnnectIon_ERROR__:{error}")


    async def send(self, message):
        if self.writer is None:
            return

        self.writer.write(f"{message}\n".encode())
        await self.writer.drain()


    async def receiver(self):
        return await self.incoming.get()

    def close(self):

        if self.writer is not None:
            self.writer.close()



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

            if username in self.chat_app.pending_requests.remove:
                self.chat_app.pending_requests.remove(username)

            self.refresh_requests()
            await self.chat_app.refresh_dms()
            return

        if event.button.id == "request_reject":

            await self.chat_app.send_command(f"/reject {username}")

            if username in self.chat_app.pending_requests:

                self.chat_app.pending_requests.remove(username)

            self.refresh_requests()


class PySyncTUUI(App):
    
    TITLE = "PySync Chat"

    CSS = """
    Screen {
        layout: vertical;
    }

    #auth_panel {
        width: 60%;
        min-width: 50;
        max-width: 90;
        height: auto;
        ,argin: 2 2;
        padding: 2;
        border: solid $primary;
    }

    #auth_title {
        text-align: center;
        width: 100%;
        margin-bottom: 2;
    }

    