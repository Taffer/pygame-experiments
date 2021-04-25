# Experiment 7 - Animated Icon
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.gfxdraw
import time
import sys

SCREEN_TITLE = 'Experiment 7 - Animated Icon'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.robot = pygame.image.load('resources/character_robot_sheet.png').convert_alpha()

        # Frame co-ordinates from character_robot_sheet.xml. Luckily they're all
        # in one row, so this is easy to loop through.
        self.frames = [self.robot.subsurface((x, 512, 96, 128)) for x in range(0, 673, 96)]
        self.idx = 0

        self.rect = self.frames[0].get_rect()
        self.rect.top = 100
        self.rect.left = 100

        self.outline = self.rect.inflate(1, 1)

        self.ticks = 0

    def draw(self):
        self.screen.fill(BLACK)

        self.screen.blit(self.frames[self.idx], self.rect)
        pygame.gfxdraw.rectangle(self.screen, self.outline, GREEN)

    def update(self, dt):
        self.ticks += dt

        if self.ticks > 1/10:  # 10 frames/second
            self.ticks -= 1/10
            self.idx += 1
            if self.idx >= len(self.frames):
                self.idx = 0


def main():
    pygame.init()

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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
