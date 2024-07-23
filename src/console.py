import code
import queue
import threading
from typing import NoReturn

from src.engine.engine import Engine


class Console:
    def __init__(self) -> None:
        self.console_queue: queue.Queue[str] = queue.Queue()

    def launch_console(self, engine: Engine) -> None:
        threading.Thread(target=lambda: self._open_console(engine)).start()

    def _open_console(self, engine: Engine) -> None:
        variables = {"m": engine, "exit": self._console_exit}
        console = code.InteractiveConsole(variables)
        print("Debugging console opened. The game is paused.")
        print("Use 'print(variable)' to see values. Example: print(score)")
        print("Type 'exit()' to return to the game.")
        try:
            console.interact(banner="")
        except SystemExit:
            pass
        print("Exiting interactive console. Resuming game.")
        self.console_queue.put("resume")

    def _console_exit(self) -> NoReturn:
        raise SystemExit
