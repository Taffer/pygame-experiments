''' Experiment 25 - FPS Counter

By Chris Herborth (https://github.com/Taffer)
MIT license, see LICENSE.md for details.
'''

import math
import pygame
import pygame.freetype
import time
import sys

SCREEN_TITLE = 'Experiment 25 - FPS Counter'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')


class FPSCounter:
    def __init__(self, screen, color):
        self.screen = screen
        self.color = color

        self.frames = 0
        self.seconds = 0

        self.font = pygame.freetype.SysFont(pygame.freetype.get_default_font(), 16)

    def draw(self):
        if self.seconds > 0:
            # The very first time this is called happens before the first call
            # to update().
            self.frames += 1
            fps = math.floor(self.frames / self.seconds)
            self.font.render_to(self.screen, (0, 0), 'FPS: {0:5}'.format(fps), self.color)

    def update(self, dt):
        self.seconds += dt


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.robot1 = pygame.image.load('resources/character_robot_jump.png').convert_alpha()
        self.rect1 = self.robot1.get_rect()
        self.rect1.top = 100
        self.rect1.left = 100

        self.robot2 = pygame.image.load('resources/character_robot_jump-2y.png').convert_alpha()
        self.rect2 = self.robot2.get_rect()
        self.rect2.top = 100
        self.rect2.left = 200

        self.area = pygame.Rect(0, 0, self.rect1.width, self.rect1.height)

        self.ticks = 0

        self.fps_counter = FPSCounter(self.screen, GREEN)

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.robot1, self.rect1)
        self.screen.blit(self.robot2, self.rect2, self.area)

        self.fps_counter.draw()

    def update(self, dt):
        self.ticks += dt

        if self.ticks > 1/60:
            self.ticks = self.ticks - 1/60

            self.area.y += 1

            if self.area.y >= 126:
                self.area.y = 0

        self.fps_counter.update(dt)


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
