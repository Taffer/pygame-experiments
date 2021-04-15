#!/usr/bin/env python3
#
# Experiment 4 - Text Entry
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import time
import sys

SCREEN_TITLE = 'Experiment 4 - Text Entry'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
WHITE = pygame.Color('white')


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.max_lines = 5
        self.max_columns = 20
        self.margin = 2

        self.dy = 0
        self.dx = 0

        self.text = []  # Completed lines of text.
        self.cursor = ''  # Incomplete line of text.

        self.font = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)
        self.dy = self.font.get_sized_height()
        rect = self.font.get_rect('M')
        self.dx = rect.width

    def draw(self):
        self.screen.fill(BLACK)

        text_x = 100
        text_y = 100

        self.font.render_to(self.screen, (10, 10), 'Press [Space] to add text.', WHITE)

        # Draw a rectangle around the text area so we can see if we go over.
        rect = pygame.Rect(text_x, text_y, self.max_columns * self.dx, self.max_lines * self.dy)
        rect.inflate(self.margin, self.margin)
        pygame.gfxdraw.rectangle(self.screen, rect, GREEN)

        delta = 0
        for line in self.text:
            self.font.render_to(self.screen, (text_x, text_y + delta), line, WHITE)
            delta += self.dy

        if len(self.cursor) > 0:
            self.font.render_to(self.screen, (text_x, text_y + delta), self.cursor, WHITE)

    def update(self, dt):
        pass


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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key == pygame.K_RETURN:
                    # Add moar text.
                    demo.text.append(demo.cursor)
                    demo.cursor = ''

                    if len(demo.text) >= demo.max_lines:
                        demo.text = demo.text[1:]
                elif event.key < 33 or event.key > 127:
                    demo.cursor += '?'
                else:
                    demo.cursor += chr(event.key)


if __name__ == '__main__':
    main()
