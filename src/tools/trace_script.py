from dataclasses import dataclass, field
import datetime
import linecache
import sys
from pathlib import Path
from typing import Any, Final

from src.main import main
from src.tools import trace_config as config
from src.tools.setup_logging import get_main_directory

exclude_patterns = config.exclude_patterns + config.custom_exclude_patterns


@dataclass
class View:
    _strings: list[str] = field(init=False, default_factory=list)

    def start_stack(self) -> None:
        self._strings.append("")

    def add_stack_line(self, filename: str, *, function_name: str) -> None:
        self._strings.append(filename + ":" + function_name + "()")

    def add_jump(self) -> None:
        self._strings.append("*")

    def add_line(self, line: str, lineno: int) -> None:
        self._strings.append("line %d: %s" % (lineno, line.rstrip()))

    def allow_flush(self) -> None:
        if len(self._strings) > 100:
            write("\n".join(self._strings))
            self._strings.clear()


i = 0
last: str | None = None
view: Final = View()
last_function_name: str | None = None
jump = False

# TODO: we should exclude first on stack patterns

this_filename = __file__.split("\\")[-1]
project_directory_name = "python_mini_metro"


def simplify_filename(co_filename: str) -> str:
    return to_unix(co_filename.split(project_directory_name)[1][1:])


def to_unix(filename: str) -> str:
    return filename.replace("\\", "/")


def traceit(frame: Any, event: Any, arg: Any) -> Any:
    global i, last, last_function_name, jump
    if event == "line":
        lineno = frame.f_lineno
        co = frame.f_code
        co_filename = to_unix(co.co_filename)
        co_name = co.co_name
        del co
        if any(pattern in co_filename for pattern in exclude_patterns) or any(
            pattern in co_name for pattern in config.function_exclude_patterns
        ):
            jump = True
            return traceit
        assert "src" in co_filename, co_filename

        # get the stack and remove if we are under custom-excluded function or filename
        stack_frame = frame
        del frame
        stack: list[tuple[str, str]] = []
        while stack_frame:
            stack_frame_co_filename = stack_frame.f_code.co_filename
            stack_frame_co_name = stack_frame.f_code.co_name
            if stack_frame_co_filename.endswith(this_filename):
                break
            stack.append(
                (simplify_filename(stack_frame_co_filename), stack_frame_co_name)
            )
            if any(
                pattern in stack_frame_co_filename
                for pattern in config.custom_exclude_patterns
            ) or any(
                pattern in stack_frame_co_name  # fmt
                for pattern in config.function_exclude_patterns
            ):
                jump = True
                return traceit

            stack_frame = stack_frame.f_back

        if jump:
            view.add_jump()
            jump = False

        i += 1
        if last != co_filename or last_function_name != co_name:
            view.start_stack()
            for item in reversed(stack):
                filename_, function_name = item
                view.add_stack_line(filename_, function_name=function_name)

        line = linecache.getline(co_filename, lineno)
        view.add_line(line, lineno)

        view.allow_flush()

        last_function_name = co_name
        last = co_filename
    return traceit


def write(text: str) -> None:
    with open(Path(get_main_directory() / ".trace"), "a") as file:
        file.write(text + "\n")


if __name__ == "__main__":
    write("")
    write("******************")
    write(str(datetime.datetime.now()))
    write("******************")
    sys.settrace(traceit)
    main()
