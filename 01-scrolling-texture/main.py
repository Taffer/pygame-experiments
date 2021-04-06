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


def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    robot1 = pygame.image.load('resources/character_robot_jump.png')
    rect1 = robot1.get_rect()
    rect1.top = 100
    rect1.left = 100

    robot2 = pygame.image.load('resources/character_robot_jump-2y.png')
    rect2 = robot2.get_rect()
    rect2.top = 100
    rect2.left = 200
    area = pygame.Rect(0, 0, rect1.width, rect1.height)
    ticks = 0

    now = time.time()
    dt = 0
    while True:
        screen.fill((0, 0, 0, 1))
        screen.blit(robot1, rect1)
        screen.blit(robot2, rect2, area)
        pygame.display.flip()

        dt = dt + time.time() - now
        now = time.time()
        if dt > 1/60:
            dt = dt - 1/60
            ticks = ticks + 1

            robot2.scroll(0, -1)

            if ticks >= 126:
                # This seems like it might be very inefficient...
                robot2 = pygame.image.load('resources/character_robot_jump-2y.png')
                ticks = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()


if __name__ == '__main__':
    main()
