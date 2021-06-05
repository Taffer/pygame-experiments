# Experiment 29 - Conversation Dialog
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import sys
import time

SCREEN_TITLE = 'Experiment 29 - Conversation Dialog'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
RED = pygame.Color('red')
WHITE = pygame.Color('white')

DIALOG_TLK = {
    'NAME': 'Call me "Tiny Cthulhu."',
    'JOB': 'I eat SOULS.',
    'SOULS': "If I eat enough of them, I'll grow up to be big and strong!",
    'BYE': "Oh, you can't leave now..."
}


class Dialog:
    def __init__(self: 'Dialog', screen: pygame.Surface, rect: pygame.Rect, font: pygame.freetype.Font, decorations: dict):
        self.screen = screen
        self.rect = rect
        self.font = font
        self.font_height = self.font.get_sized_glyph_height()

        rect = self.font.get_rect(' ')
        self.space_width = rect.width

        self.decorations = decorations
        self.decoration_rects = {k: v.get_rect() for k, v in self.decorations.items()}
        self.ui_batch = self.setup_ui_batch()

        # font_height * 2 so we can draw input text with a font_height pad
        # above it.
        self.textrect = pygame.Rect(self.decoration_rects['avatar'].x + self.decoration_rects['avatar'].width,
                                    self.decoration_rects['avatar'].y,
                                    self.decoration_rects['top-middle'].width - self.decoration_rects['avatar'].width,
                                    self.decoration_rects['mid-left'].height - self.font_height * 2)
        self.inputrect = pygame.Rect(self.textrect.x, self.textrect.y + self.textrect.height + self.font_height,
                                     self.textrect.width, self.font_height)

        self.text = []
        self.add_text('Type keywords like NAME, or JOB.')
        self.input = '> '

    def setup_ui_batch(self):
        # WARNING: This function also mutates the decorations and their rects.
        middle_width = self.rect.width - self.decoration_rects['top-left'].width - self.decoration_rects['top-right'].width
        middle_height = self.rect.height - self.decoration_rects['top-left'].height - self.decoration_rects['bot-left'].height

        # Scale the middle bars to the required size; depending on the texture,
        # this could look terrible...
        self.decorations['top-middle'] = pygame.transform.smoothscale(self.decorations['top-middle'],
                                                                      (middle_width, self.decoration_rects['top-middle'].height))
        self.decorations['bot-middle'] = pygame.transform.smoothscale(self.decorations['bot-middle'],
                                                                      (middle_width, self.decoration_rects['bot-middle'].height))
        self.decorations['mid-left'] = pygame.transform.smoothscale(self.decorations['mid-left'],
                                                                    (self.decoration_rects['mid-left'].width, middle_height))
        self.decorations['mid-right'] = pygame.transform.smoothscale(self.decorations['mid-right'],
                                                                     (self.decoration_rects['mid-right'].width, middle_height))
        self.decoration_rects['top-middle'] = self.decorations['top-middle'].get_rect()
        self.decoration_rects['bot-middle'] = self.decorations['bot-middle'].get_rect()
        self.decoration_rects['mid-left'] = self.decorations['mid-left'].get_rect()
        self.decoration_rects['mid-right'] = self.decorations['mid-right'].get_rect()

        # Position all the rects.
        self.decoration_rects['top-left'].x = self.rect.x
        self.decoration_rects['top-left'].y = self.rect.y
        self.decoration_rects['top-middle'].x = self.decoration_rects['top-left'].x + self.decoration_rects['top-left'].width
        self.decoration_rects['top-middle'].y = self.rect.y
        self.decoration_rects['top-right'].x = self.decoration_rects['top-middle'].x + self.decoration_rects['top-middle'].width
        self.decoration_rects['top-right'].y = self.rect.y
        self.decoration_rects['mid-left'].x = self.rect.x
        self.decoration_rects['mid-left'].y = self.decoration_rects['top-left'].y + self.decoration_rects['top-left'].height
        self.decoration_rects['mid-right'].x = self.decoration_rects['top-right'].x
        self.decoration_rects['mid-right'].y = self.decoration_rects['top-right'].y + self.decoration_rects['top-right'].height
        self.decoration_rects['bot-left'].x = self.rect.x
        self.decoration_rects['bot-left'].y = self.decoration_rects['mid-left'].y + self.decoration_rects['mid-left'].height
        self.decoration_rects['bot-middle'].x = self.decoration_rects['bot-left'].x + self.decoration_rects['bot-left'].width
        self.decoration_rects['bot-middle'].y = self.decoration_rects['bot-left'].y
        self.decoration_rects['bot-right'].x = self.decoration_rects['bot-middle'].x + self.decoration_rects['bot-middle'].width
        self.decoration_rects['bot-right'].y = self.decoration_rects['bot-left'].y
        self.decoration_rects['avatar'].x = self.decoration_rects['top-left'].x + self.decoration_rects['top-left'].width
        self.decoration_rects['avatar'].y = self.decoration_rects['top-left'].y + self.decoration_rects['top-left'].height

        ui_batch = (
            (self.decorations['top-left'], self.decoration_rects['top-left']),
            (self.decorations['top-middle'], self.decoration_rects['top-middle']),
            (self.decorations['top-right'], self.decoration_rects['top-right']),
            (self.decorations['mid-left'], self.decoration_rects['mid-left']),
            (self.decorations['mid-right'], self.decoration_rects['mid-right']),
            (self.decorations['bot-left'], self.decoration_rects['bot-left']),
            (self.decorations['bot-middle'], self.decoration_rects['bot-middle']),
            (self.decorations['bot-right'], self.decoration_rects['bot-right']),

            (self.decorations['avatar'], self.decoration_rects['avatar']),
            )
        return ui_batch

    def add_text(self, line):
        rect = self.font.get_rect(line)
        if rect.width <= self.textrect.width:
            self.text.append(line)
        else:
            parts = line.split()
            tmp_str = parts[0]
            rect = self.font.get_rect(tmp_str)
            for i in parts[1:]:
                i_rect = self.font.get_rect(i)
                if rect.width + self.space_width + i_rect.width < self.textrect.width:
                    tmp_str += ' ' + i
                else:
                    self.text.append(tmp_str)
                    tmp_str = i
                rect = self.font.get_rect(tmp_str)
            if len(tmp_str) > 0:
                self.text.append(tmp_str)

        while len(self.text) * self.font_height > self.textrect.height:
            self.text = self.text[1:]

    def draw(self: 'Dialog') -> None:
        self.screen.blits(self.ui_batch)

        # pygame.gfxdraw.rectangle(self.screen, self.textrect, GREEN)
        # pygame.gfxdraw.rectangle(self.screen, self.inputrect, RED)

        text_y = self.textrect.y
        for line in self.text:
            self.font.render_to(self.screen, (self.textrect.x, text_y), line, WHITE)
            text_y += self.font_height

        self.font.render_to(self.screen, (self.inputrect.x, self.inputrect.y), self.input, WHITE)

    def update(self: 'Dialog', dt: float) -> None:
        pass

    def keydown(self: 'Dialog', key):
        if key == pygame.K_RETURN:
            question = self.input[2:]
            self.add_text(self.input)
            self.input = '> '

            if question in DIALOG_TLK:
                self.add_text(DIALOG_TLK[question])
            else:
                self.add_text("I don't know anything about {0}.".format(question))
        elif key == pygame.K_BACKSPACE:
            if len(self.input) > 2:
                self.input = self.input[:-1]
        elif key >= ord('a') and key <= ord('z'):
            self.input += chr(key - 32)
        else:
            try:
                self.input += chr(key)
            except ValueError:
                pass  # Shift, Function keys, etc.


class Demo:
    def __init__(self: 'Demo', screen: pygame.Surface) -> None:
        self.screen = screen

        self.font = pygame.freetype.Font('resources/fonts/LiberationSerif-Bold.ttf', 16)
        self.paper_image = pygame.image.load('resources/rpg_gui_v1/paper background.png').convert_alpha()
        self.ui_image = pygame.image.load('resources/rpg_gui_v1/RPG_GUI_v1.png').convert_alpha()
        self.avatar = pygame.image.load('resources/cuttlefishsmallicon.png').convert_alpha()

        self.ticks = 0

        # Set up subsurfaces for the UI parts.
        corner_wh = 24
        middle_width = 73
        middle_height = 55

        # These quads are a bit painful, the original isn't set up as a texture
        # atlas.
        #
        # top-left corner piece: 856,189, 24x24
        # top-middle: 893,189, 73x24
        # top-rignt: 978,189, 24x24
        # middle-left: 856,227, 24x55
        # middle-right: 978,227, 24x55
        # bottom-left: 856,294, 24x24
        # bottom-middle: 893,294, 73x24
        # bottom-right: 978,294, 24x24
        rect = pygame.Rect(856, 189, corner_wh, corner_wh)
        tl = self.ui_image.subsurface(rect)

        rect = pygame.Rect(893, 189, middle_width, corner_wh)
        tm = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 189, corner_wh, corner_wh)
        tr = self.ui_image.subsurface(rect)

        rect = pygame.Rect(856, 227, corner_wh, middle_height)
        ml = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 227, corner_wh, middle_height)
        mr = self.ui_image.subsurface(rect)

        rect = pygame.Rect(856, 294, corner_wh, corner_wh)
        bl = self.ui_image.subsurface(rect)

        rect = pygame.Rect(893, 294, middle_width, corner_wh)
        bm = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 294, corner_wh, corner_wh)
        br = self.ui_image.subsurface(rect)

        decorations = {
            'top-left': tl,
            'top-middle': tm,
            'top-right': tr,

            'mid-left': ml,
            'mid-right': mr,

            'bot-left': bl,
            'bot-middle': bm,
            'bot-right': br,

            'avatar': self.avatar
        }

        self.dialog = Dialog(self.screen, pygame.Rect(100, 100, 320, 240), self.font, decorations)

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        self.dialog.draw()

        self.font.render_to(self.screen, (10, 10), 'Type to talk, press Escape to exit.', WHITE)

    def update(self: 'Demo', dt: float) -> None:
        self.ticks += dt
        if self.ticks > 1/20:
            self.ticks -= 1/20

    def keydown(self: 'Demo', key):
        self.dialog.keydown(key)


def main() -> None:
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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    playing = False
                else:
                    demo.keydown(event.key)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
