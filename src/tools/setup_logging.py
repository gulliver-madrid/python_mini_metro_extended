import logging
from pathlib import Path, PurePath

_MAIN_DIRECTORY = PurePath(__file__).parents[2]


def get_main_directory() -> PurePath:
    return _MAIN_DIRECTORY


def configure_logger(name: str, level: int = logging.DEBUG) -> logging.Logger:
    """Configure a logger and send its output to a file"""
    log_file_name = f"{name}.log"
    # Create a specific logger
    logger = logging.getLogger(name)
    logger.propagate = False  # Prevent propagation to the root logger
    logger.setLevel(level)  # Set the logger level

    # Create a specific FileHandler to write to a file
    path = Path(get_main_directory()) / "logs"  # pragma: no mutate
    if not path.exists():
        path.mkdir()
    file_handler = logging.FileHandler(path / log_file_name, encoding="utf-8")
    file_handler.setLevel(level)  # Set the FileHandler level

    # Create a formatter and add it to the FileHandler
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Add the FileHandler to the logger
    logger.addHandler(file_handler)
    logger.info("\n")
    logger.info("START")

    return logger
