import code
import queue
import threading
from typing import NoReturn

from src.engine.engine import Engine


class Console:
    def __init__(self) -> None:
        self._console_queue: queue.Queue[str] = queue.Queue()

    def launch_console(self, engine: Engine) -> None:
        threading.Thread(target=lambda: self._open_console(engine)).start()

    def try_get_command(self) -> str | None:
        try:
            cmd = self._console_queue.get_nowait()
            assert isinstance(cmd, str)
        except queue.Empty:
            return None
        return cmd

    def _open_console(self, engine: Engine) -> None:
        variables = {"e": engine, "engine": engine, "exit": self._console_exit}
        console = code.InteractiveConsole(variables)
        print("Debugging console opened. The game is paused.")
        print("Use 'print(variable)' to see values. Example: print(score)")
        print("Type 'exit()' to return to the game.")
        try:
            console.interact(banner="")
        except SystemExit:
            pass
        print("Exiting interactive console. Resuming game.")
        self._console_queue.put("resume")

    def _console_exit(self) -> NoReturn:
        raise SystemExit
