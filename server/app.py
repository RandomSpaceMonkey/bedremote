from typing import Dict, Callable
from functools import wraps
import inspect
import math
import asyncio
import json
import websockets
import pyautogui
import websockets.server

Command = Dict[str, str]
EventHandler = Callable[[Command], None] | Callable[[], None]


class Server:
    def __init__(self):
        self.handlers: Dict[str, EventHandler] = {}

    @staticmethod
    def handles(event_type: str):
        def add_handler(method: Callable):
            @wraps(method)
            def wrapper(self, *args, **kwargs):
                self.handlers[event_type] = method
                method(self, *args, **kwargs)
            return wrapper
        return add_handler

    @staticmethod
    @handles('MouseMove')
    def handle_mouse_move(cmd: Command):
        x, y = pyautogui.position()
        new_x = 5 * math.sin(math.radians(int(cmd['direction'])))
        new_y = -5 * math.cos(math.radians(int(cmd['direction'])))  # multiply by negative since larger y values go
        # down in pyautogui - https://pyautogui.readthedocs.io/en/latest/mouse.html?highlight=mouse
        pyautogui.moveTo(x + new_x, y + new_y)

    @staticmethod
    @handles('MouseClick')
    def handle_mouse_click():
        pyautogui.leftClick()

    @staticmethod
    @handles('Pause')
    def handle_pause():
        pyautogui.press('space')

    async def main_handler(self, websocket: websockets.server.WebSocketServerProtocol):
        async for message in websocket:
            try:
                print(self.handlers)
                cmd: Command = json.loads(message)
                handler = self.handlers.get(cmd['type'])
                if not handler:
                    raise Exception(f"No handler for message type {cmd['type']}")
                sig = inspect.signature(handler)
                if sig.parameters:
                    handler(cmd)
                    return
                handler()
            except Exception as e:
                print(f'{type(e).__name__}: {e}')

    async def run(self):
        async with websockets.serve(self.main_handler, '', 8000):
            await asyncio.Future()


if __name__ == '__main__':
    server = Server()
    asyncio.run(server.run())
