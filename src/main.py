import pygame

from src.config import Config, framerate, screen_color
from src.event.convert import convert_pygame_event
from src.mediator.mediator import Mediator
from src.reactor import UI_Reactor


def main() -> None:
    # init
    pygame.init()

    # settings
    flags = pygame.SCALED

    # game constants initialization
    screen = pygame.display.set_mode(
        (Config.screen_width, Config.screen_height), flags, vsync=1
    )
    clock = pygame.time.Clock()
    pygame.display.set_caption("Python Minimetro")

    mediator = Mediator()
    mediator.set_clock(clock)
    reactor = UI_Reactor(mediator)

    while True:
        dt_ms = clock.tick(framerate)
        mediator.increment_time(dt_ms)
        screen.fill(screen_color)
        mediator.render(screen)

        # react to user interaction
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                raise SystemExit
            else:
                event = convert_pygame_event(pygame_event)
                reactor.react(event)

        pygame.display.flip()


if __name__ == "__main__":
    main()
