#!/usr/bin/env python3
'''
By Chris Herborth (https://github.com/Taffer)
MIT license, see LICENSE.md for details.
'''

import pygame
import pygame.freetype
import pygame.gfxdraw
import time
import sys

SCREEN_TITLE = 'Experiment 3 - Text Variable'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
WHITE = pygame.Color('white')

TEXT = [
    'Next is too long:',
    'The quick brown fox jumps over the lazy dog.',
    'Better split.',
    'That text was too long. What about this line?',
    'Oops, so was that.',
    'We need to fix it.'
]


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.buff = []

        self.max_lines = 5
        self.max_columns = 20
        self.margin = 2

        self.text_x = 100
        self.text_y = 100

        self.dy = 0
        self.dx = 0

        self.font = pygame.freetype.Font('resources/LiberationSerif-Bold.ttf', 16)
        self.dy = self.font.get_sized_height()
        rect = self.font.get_rect('M')
        self.dx = rect.width

        rect = self.font.get_rect(' ')
        self.space_width = rect.width

        self.max_width = self.max_columns * self.dx

    def draw(self):
        self.screen.fill(BLACK)

        self.font.render_to(self.screen, (10, 10), 'Press [Space] to add text.', WHITE)

        # Draw a rectangle around the text area so we can see if we go over.
        rect = pygame.Rect(self.text_x, self.text_y, self.max_columns * self.dx, self.max_lines * self.dy)
        rect.inflate(self.margin, self.margin)
        pygame.gfxdraw.rectangle(self.screen, rect, GREEN)

        delta = 0
        for line in self.buff:
            self.font.render_to(self.screen, (self.text_x, self.text_y + delta), line, WHITE)
            delta += self.dy

    def update(self, dt):
        pass

    def add_text(self, line):
        rect = self.font.get_rect(line)
        if rect.width <= self.max_width:
            self.buff.append(line)
        else:
            parts = line.split()
            tmp_str = parts[0]
            rect = self.font.get_rect(tmp_str)
            for i in parts[1:]:
                i_rect = self.font.get_rect(i)
                if rect.width + self.space_width + i_rect.width < self.max_width:
                    tmp_str += ' ' + i
                else:
                    self.buff.append(tmp_str)
                    tmp_str = i
                rect = self.font.get_rect(tmp_str)
            if len(tmp_str) > 0:
                self.buff.append(tmp_str)

        while len(self.buff) > self.max_lines:
            self.buff = self.buff[1:]


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    demo = Demo(screen)

    now = time.time()
    dt = 0

    text_idx = 0

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
                elif event.key == pygame.K_SPACE:
                    # Add moar text.
                    demo.add_text(TEXT[text_idx])
                    text_idx += 1
                    if text_idx >= len(TEXT):
                        text_idx = 0

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
