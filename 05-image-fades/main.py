#!/usr/bin/env python3
''' Experiment 1 - Scrolling Texture

By Chris Herborth (https://github.com/Taffer)
MIT license, see LICENSE.md for details.
'''

import pygame
import time
import sys

SCREEN_TITLE = 'Experiment 5 - Image Fades'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    robot1 = pygame.image.load('resources/character_robot_jump.png')
    rect1 = robot1.get_rect()
    rect1.top = 100
    rect1.left = 100

    rect2 = robot1.get_rect()
    alpha2 = pygame.Surface((rect2.width, rect2.height))
    alpha2.fill((0, 0, 0, 0))
    alpha2.set_alpha(255)
    rect2.top = 100
    rect2.left = 250

    now = time.time()
    dt = 0
    alpha = 255
    while True:
        screen.fill((0, 0, 0, 1))
        screen.blit(robot1, rect1)  # Normal sprite

        screen.blit(robot1, rect2)  # Linear fade
        screen.blit(alpha2, rect2)

        pygame.display.flip()

        dt = dt + time.time() - now
        now = time.time()
        if dt > 1/60:
            dt = dt - 1/60
            alpha = alpha - 256/120
            if alpha < 0:
                alpha = 255
            alpha2.set_alpha(alpha)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()


if __name__ == '__main__':
    main()
