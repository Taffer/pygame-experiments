# Experiment 7 - Animated Icon
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.gfxdraw
import time
import sys

SCREEN_TITLE = 'Experiment 5 - Image Fades'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    robot = pygame.image.load('resources/character_robot_sheet.png')

    # Frame co-ordinates from character_robot_sheet.xml. Luckily they're all
    # in one row, so this is easy to loop through.
    frames = [robot.subsurface((x, 512, 96, 128)) for x in range(0, 673, 96)]
    idx = 0

    rect = frames[0].get_rect()
    rect.top = 100
    rect.left = 100

    outline = rect.inflate(1, 1)

    now = time.time()
    dt = 0

    while True:
        screen.fill(BLACK)

        screen.blit(frames[idx], rect)
        pygame.gfxdraw.rectangle(screen, outline, GREEN)
        pygame.display.flip()

        dt = dt + time.time() - now
        now = time.time()
        if dt > 1/10:  # 10 frames/second
            dt -= 1/10
            idx += 1
            if idx >= len(frames):
                idx = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                sys.exit()


if __name__ == '__main__':
    main()
