import random
import sys

import numpy as np
import pygame

from src.config import Config, screen_color
from src.engine.engine import Engine
from src.event.convert import convert_pygame_event
from src.reactor import UI_Reactor


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
        engine.increment_time(dt_ms)
        screen.fill(screen_color)
        engine.render(screen)

        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                engine.exit()

            event = convert_pygame_event(pygame_event)
            reactor.react(event)

        pygame.display.flip()


if __name__ == "__main__":
    main()
