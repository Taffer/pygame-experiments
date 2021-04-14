#!/usr/bin/env python3
''' Experiment 1 - Scrolling Texture

By Chris Herborth (https://github.com/Taffer)
MIT license, see LICENSE.md for details.
'''

import pygame
import time
import sys

SCREEN_TITLE = 'Experiment 1 - Scrolling Texture'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')


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

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.robot1, self.rect1)
        self.screen.blit(self.robot2, self.rect2, self.area)

    def update(self, dt):
        self.ticks += dt

        if self.ticks > 1/60:
            self.ticks = self.ticks - 1/60

            self.area.y += 1

            if self.area.y >= 126:
                self.area.y = 0


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    demo = Demo(screen)

    now = time.time()
    dt = 0
    while True:
        demo.draw()
        pygame.display.flip()

        dt = time.time() - now
        now = time.time()

        demo.update(dt)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()


if __name__ == '__main__':
    main()
