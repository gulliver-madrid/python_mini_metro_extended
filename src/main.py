import random
import sys
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
    pygame.init()

    flags = pygame.SCALED
    screen = pygame.display.set_mode(
        (Config.screen_width, Config.screen_height), flags, vsync=1
    )

    args = sys.argv[1:]
    if args:
        assert len(args) == 1
        seed = int(args[0])
        assert 0 <= seed <= 999
    else:
        seed = random.randint(0, 999)
    print(f"Random seed: {seed}")
    random.seed(seed)
    np.random.seed(seed)

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
