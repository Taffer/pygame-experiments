# Experiment 8 - Styled Text
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import time
import sys

SCREEN_TITLE = 'Experiment 8 - Styled Text'

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


class StyledText:
    def __init__(self, text, font, color):
        self.text = text
        self.font = font
        self.color = color

    def get_height(self):
        return self.font.get_sized_height()

    def get_width(self):
        rect = self.font.get_rect(self.text)
        return rect.width

    def draw(self, surface, x, y):
        self.font.render_to(surface, (x, y), self.text, self.color)


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
        self.mono = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)
        self.dy = max(self.font.get_sized_height(), self.mono.get_sized_height())
        rect_serif = self.font.get_rect('M')
        rect_mono = self.mono.get_rect('M')
        self.dx = max(rect_serif.width, rect_mono.width)

        rect_serif = self.font.get_rect(' ')
        rect_mono = self.mono.get_rect(' ')
        self.space_width = max(rect_serif.width, rect_mono.width)

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
            x_delta = 0
            for w in line:
                w.draw(self.screen, self.text_x + x_delta, self.text_y + delta)
                x_delta += w.get_width()
            delta += self.dy

    def update(self, dt):
        pass

    def add_text(self, line):
        width = 0
        pieces = []
        for w in line.split():
            w += ' '
            font = None
            if random.randint(0, 1) == 0:
                font = self.font
            else:
                font = self.mono
            color = pygame.Color(random.randint(128, 255), random.randint(128, 255), random.randint(128, 255), 255)

            styled = StyledText(w, font, color)

            styled_width = styled.get_width()
            if width + styled_width < self.max_width:
                pieces.append(styled)
                width += styled_width
            else:
                self.buff.append(pieces)
                pieces = [styled]
                width = styled_width

        if len(pieces) > 0:
            self.buff.append(pieces)

        while len(self.buff) > self.max_lines:
            self.buff = self.buff[1:]


def main():
    pygame.init()
    random.seed(time.time())

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
