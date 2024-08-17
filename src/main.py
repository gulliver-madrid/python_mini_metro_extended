import argparse
import random
import time

import numpy as np
import pygame

from src.config import Config, screen_color
from src.engine.engine import Engine
from src.event.convert import convert_pygame_event
from src.reactor import UI_Reactor
from src.tools.setup_logging import configure_logger

logger = configure_logger("main")

DEBUG_TIME = False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Python implementation of the Mini Metro game."
    )

    parser.add_argument("-s", "--seed", type=int, help="Random seed")

    parser.add_argument("-st", "--stations", type=int, help="Number of stations")

    args = parser.parse_args()

    random_seed = args.seed
    if random_seed is not None:
        assert 0 <= random_seed <= 999
    else:
        random_seed = random.randint(0, 999)

    if args.stations is not None:
        assert args.stations >= 0
        Config.num_stations = args.stations

    print(f"Random seed: {random_seed}")
    print(f"Number of stations: {Config.num_stations}")

    random.seed(random_seed)
    np.random.seed(random_seed)

    pygame.init()

    flags = pygame.SCALED
    screen = pygame.display.set_mode(
        (Config.screen_width, Config.screen_height), flags, vsync=1
    )

    clock = pygame.time.Clock()
    pygame.display.set_caption("Python Minimetro")

    engine = Engine()
    engine.set_clock(clock)
    reactor = UI_Reactor(engine)

    while True:
        dt_ms = clock.tick(Config.framerate)
        t = time.time()
        logger.info(f"{dt_ms=}")
        logger.info(f"fps: {round(clock.get_fps(), 2)}\n")
        engine.increment_time(dt_ms)
        screen.fill(screen_color)
        engine.render(screen)

        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                engine.exit()

            event = convert_pygame_event(pygame_event)
            reactor.react(event)

        pygame.display.flip()

        if Config.stop:
            breakpoint()

        tt = time.time() - t
        if DEBUG_TIME:
            if tt > 0.06:
                print(f"{tt=}")


if __name__ == "__main__":
    main()
