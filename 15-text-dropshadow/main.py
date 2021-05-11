# Experiment 15 - Text Dropshadows
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import time
import sys

SCREEN_TITLE = 'Experiment 15 - Text Dropshadows'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationSerif-Bold.ttf', 16)
        self.mono = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)

        self.font_height = self.font.get_sized_height()
        self.mono_height = self.mono.get_sized_height()

        self.grass = pygame.image.load('resources/grass.png')
        grass_rect = self.grass.get_rect()
        self.grass_batch = []
        for y in range(0, 720, 32):
            for x in range(0, 1280, 32):
                dest = pygame.Rect(x, y, grass_rect.width, grass_rect.height)
                self.grass_batch.append((self.grass, dest, grass_rect))

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blits(self.grass_batch)

        # Variable width font.
        y = 10
        self.font.render_to(self.screen, (10, y), 'Plain white text is hard to read on a light background.', WHITE)

        # Drop-shadow at 0, +1:
        y += int(self.font_height * 1.5)
        text = "Single pixel lower drop-shadow, hopefully it's better."
        self.font.render_to(self.screen, (10, y + 1), text, BLACK)
        self.font.render_to(self.screen, (10, y), text, WHITE)

        # Drop-shadow at +1, +1:
        y += int(self.font_height * 1.5)
        text = "Single pixel lower-right drop-shadow, hopefully it's better."
        self.font.render_to(self.screen, (10 + 1, y + 1), text, BLACK)
        self.font.render_to(self.screen, (10, y), text, WHITE)

        # Double drop-shadow at 0, +1 and +1, +1
        y += int(self.font_height * 1.5)
        text = "Double pixel lower and lower-right drop-shadow, hopefully it's better."
        for i in range(2):
            self.font.render_to(self.screen, (10 + i, y + 1), text, BLACK)
        self.font.render_to(self.screen, (10, y), text, WHITE)

        # Triple drop-shadow at (-1, +1), (0, +1) and (+1, +1)
        y += int(self.font_height * 1.5)
        text = "Triple pixel lower-left, lower, and lower-right drop-shadow, hopefully it's better."
        for i in range(-1, 2):
            self.font.render_to(self.screen, (10 + i, y + 1), text, BLACK)
        self.font.render_to(self.screen, (10, y), text, WHITE)

        # Go nuts, draw at one pixel all around.
        y += int(self.font_height * 1.5)
        text = "Four drop-shadows, one in each corner, this is the best."
        for dy in range(-1, 2, 2):
            for dx in range(-1, 2, 2):
                self.font.render_to(self.screen, (10 + dx, y + dy), text, BLACK)
        self.font.render_to(self.screen, (10, y), text, WHITE)

        # Mono width font.
        y += int(self.font_height * 1.5)
        self.mono.render_to(self.screen, (10, y), 'Plain white text is hard to read on a light background.', WHITE)

        # Drop-shadow at 0, +1:
        y += int(self.font_height * 1.5)
        text = "Single pixel lower drop-shadow, hopefully it's better."
        self.mono.render_to(self.screen, (10, y + 1), text, BLACK)
        self.mono.render_to(self.screen, (10, y), text, WHITE)

        # Drop-shadow at +1, +1:
        y += int(self.font_height * 1.5)
        text = "Single pixel lower-right drop-shadow, hopefully it's better."
        self.mono.render_to(self.screen, (10 + 1, y + 1), text, BLACK)
        self.mono.render_to(self.screen, (10, y), text, WHITE)

        # Double drop-shadow at 0, +1 and +1, +1
        y += int(self.font_height * 1.5)
        text = "Double pixel lower and lower-right drop-shadow, hopefully it's better."
        for i in range(2):
            self.mono.render_to(self.screen, (10 + i, y + 1), text, BLACK)
        self.mono.render_to(self.screen, (10, y), text, WHITE)

        # Triple drop-shadow at (-1, +1), (0, +1) and (+1, +1)
        y += int(self.font_height * 1.5)
        text = "Triple pixel lower-left, lower, and lower-right drop-shadow, hopefully it's better."
        for i in range(-1, 2):
            self.mono.render_to(self.screen, (10 + i, y + 1), text, BLACK)
        self.mono.render_to(self.screen, (10, y), text, WHITE)

        # Go nuts, draw at one pixel all around.
        y += int(self.font_height * 1.5)
        text = "Four drop-shadows, one in each corner, this is the best."
        for dy in range(-1, 2, 2):
            for dx in range(-1, 2, 2):
                self.mono.render_to(self.screen, (10 + dx, y + dy), text, BLACK)
        self.mono.render_to(self.screen, (10, y), text, WHITE)

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
