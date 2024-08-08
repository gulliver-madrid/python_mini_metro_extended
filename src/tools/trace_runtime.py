import traceback


def print_stack() -> None:
    frames = traceback.extract_stack()[:-1]
    if frames[0].name == "<module>":
        frames = frames[1:]
    for frame in frames:
        print(frame.name)
