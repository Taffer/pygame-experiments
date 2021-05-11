# Experiment 16 - How to Joystick
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import time
import sys

SCREEN_TITLE = 'Experiment 16 - How to Joystick'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.mono = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)

    def draw(self):
        self.screen.fill(BLACK)

        self.mono.render_to(self.screen, (10, 10), 'Move your joystick, press Esc to exit.', WHITE)

        found = pygame.joystick.get_count()
        self.mono.render_to(self.screen, (10, 30), f'Found {found} joystick(s).', WHITE)

        if found > 0:
            joystick = pygame.joystick.Joystick(0)  # This demo only supports the first joystick.
            self.mono.render_to(self.screen, (10, 50), 'Joystick #1:', WHITE)
            self.mono.render_to(self.screen, (20, 70), joystick.get_name(), WHITE)
            self.mono.render_to(self.screen, (20, 90), joystick.get_guid(), WHITE)

            y = 130
            for i in range(joystick.get_numaxes()):
                value = joystick.get_axis(i)
                self.mono.render_to(self.screen, (20, y), f'Axis {i}: {value}', WHITE)
                y += 20

            y += 20
            for i in range(joystick.get_numbuttons()):
                value = joystick.get_button(i)
                if value:
                    self.mono.render_to(self.screen, (20, y), f'Button {i}: Down', WHITE)
                else:
                    self.mono.render_to(self.screen, (20, y), f'Button {i}: Up', WHITE)
                y += 20

            y += 20
            for i in range(joystick.get_numhats()):
                value = joystick.get_hat(i)
                self.mono.render_to(self.screen, (20, y), f'Hat {i}: {value}', WHITE)
                y += 20

    def update(self, dt):
        pass


def main():
    pygame.init()
    random.seed(time.time())

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    demo = Demo(screen)

    now = time.time()
    dt = 0

    playing = True

    while playing:
        demo.draw()
        pygame.display.flip()

        dt = time.time() - now
        now = time.time()

        demo.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    playing = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
