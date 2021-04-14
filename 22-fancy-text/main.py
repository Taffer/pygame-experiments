# Experiment 11 - Tilemap
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import re
import sys
import time

SCREEN_TITLE = 'Experiment 22 - Fancy Text'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
WHITE = pygame.Color('white')

FORMATTED_TEXT = [
    'Hello world!',
    'This text is plain, with no formatting.',
    'This text sets {color=#ff0000}foreground{/color} colour.',
    'You can set {bg=#0000ff}background{/bg} as well.',
    'Or set {bg=#0000ff}{color=#ff0000}both{/color}{/bg} at once.',
    'Does {color=#00ff00}{bg=#ff00ff}order{/bg}{/color} matter?',
    'Some {s}strong{/s} text and {o}oblique{/o} text!',
]

BG_SETTER = re.compile(r'(.*){bg=(#[A-Fa-f0-9]+)}(.*){/bg}(.*)')
COLOR_SETTER = re.compile(r'(.*){color=(#[A-Fa-f0-9]+)}(.*){/color}(.*)')
OBLIQUE_SETTER = re.compile(r'(.*){o}(.*){/o}(.*)')
STRONG_SETTER = re.compile(r'(.*){s}(.*){/s}(.*)')


class TextView:
    def __init__(self, rect: pygame.Rect, font: pygame.freetype.Font, fgcolor: pygame.Color, bgcolor: pygame.Color):
        self.rect = rect
        self.outline = rect.inflate(2, 2)

        self.font = font
        self.line_spacing = int(font.get_sized_height() * 1.1)

        self.fgcolor = fgcolor
        self.bgcolor = bgcolor

        rect = font.get_rect(' ')
        self.space_width = rect.width

        self.text = []  # Chunks are (text, rect, font, fgcolor, bgcolor) tuples

    def draw(self, screen: pygame.Surface):
        pygame.gfxdraw.rectangle(screen, self.outline, GREEN)
        x = self.rect.x
        y = self.rect.y + self.line_spacing
        for chunk in self.text:  # (w, self.font.get_rect(w), style, fgcolor, bgcolor)
            word = chunk[0]
            rect = pygame.Rect(chunk[1])
            style = chunk[2]
            fgcolor = chunk[3]
            bgcolor = chunk[4]
            if (x - self.rect.x + rect.width) > self.rect.width:
                x = self.rect.x
                y += self.line_spacing
            rect.x = x
            rect.y = y
            prev_style = self.font.style
            self.font.style = style
            self.font.render_to(screen, rect, word, fgcolor, bgcolor)
            self.font.style = prev_style
            x += rect.width + self.space_width

    def add_text(self, text: str):
        words = text.split()
        for w in words:
            fgcolor = self.fgcolor
            bgcolor = self.bgcolor
            style = pygame.freetype.STYLE_DEFAULT

            m = BG_SETTER.match(w)
            if m:
                parts = m.groups()
                bgcolor = pygame.Color(parts[1])
                w = parts[0] + parts[2] + parts[3]

            m = COLOR_SETTER.match(w)
            if m:
                parts = m.groups()
                fgcolor = pygame.Color(parts[1])
                w = parts[0] + parts[2] + parts[3]

            m = OBLIQUE_SETTER.match(w)
            if m:
                parts = m.groups()
                style = pygame.freetype.STYLE_OBLIQUE
                w = parts[0] + parts[1] + parts[2]

            m = STRONG_SETTER.match(w)
            if m:
                parts = m.groups()
                style = pygame.freetype.STYLE_STRONG
                w = parts[0] + parts[1] + parts[2]

            self.text.append((w, self.font.get_rect(w), style, fgcolor, bgcolor))


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationSerif-Bold.ttf', 16)
        self.font.origin = True

        self.textview = TextView(pygame.Rect(100, 100, 800, 600), self.font, WHITE, BLACK)

    def draw(self):
        self.screen.fill(BLACK)
        self.font.render_to(self.screen, (10, 10), 'Press any key to add text.', WHITE)
        self.textview.draw(self.screen)

    def update(self, dt):
        pass


def main():
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(SCREEN_TITLE)

    demo = Demo(screen)

    now = time.time()
    dt = 0

    add_idx = 0

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
                elif event.key == pygame.K_SPACE:
                    demo.textview.add_text(FORMATTED_TEXT[add_idx])
                    add_idx += 1
                    if add_idx >= len(FORMATTED_TEXT):
                        add_idx = 0


if __name__ == '__main__':
    main()
