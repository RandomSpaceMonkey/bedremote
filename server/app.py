from typing import Dict, Callable
import math
import asyncio
import json
import websockets
import pyautogui
import websockets.server

pyautogui.FAILSAFE = False
Command = Dict[str, str]
EventHandler = Callable[[Command], None]


class Server:
    def __init__(self):
        self.handlers: Dict[str, EventHandler] = {
            'MouseMove': self.handle_mouse_move,
            'MouseClick': self.handle_mouse_click,
        }

    @staticmethod
    def handle_mouse_move(cmd: Command):
        x, y = pyautogui.position()
        degrees = math.radians(int(cmd['direction']) + 90)  # nipple.js x axis is horizontal meaning
        # 0 degrees is to the right
        new_x = 50 * math.sin(degrees)
        new_y = 50 * math.cos(degrees)  # multiply by negative since larger y values go
        # down in pyautogui - https://pyautogui.readthedocs.io/en/latest/mouse.html?highlight=mouse
        pyautogui.moveTo(x + new_x, y + new_y)

    @staticmethod
    def handle_mouse_click(cmd: Command):
        if cmd['side'] == 'left':
            pyautogui.leftClick()
            return
        pyautogui.rightClick()

    async def main_handler(self, websocket: websockets.server.WebSocketServerProtocol):
        try:
            async for message in websocket:
                cmd: Command = json.loads(message)
                handler = self.handlers.get(cmd['type'])
                if not handler:
                    raise Exception(f"No handler for message type {cmd['type']}")
                handler(cmd)
        except Exception as e:
            print(f'{type(e).__name__}: {e}')

    async def run(self):
        async with websockets.serve(self.main_handler, '', 50000):
            print("server running on port 50000")
            await asyncio.Future()


if __name__ == '__main__':
    server = Server()
    asyncio.run(server.run())
