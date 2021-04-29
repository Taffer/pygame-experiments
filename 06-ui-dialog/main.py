# Experiment 6 - UI Dialog
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

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

        self.font = pygame.freetype.Font('resources/fonts/LiberationSerif-Bold.ttf', 16)
        self.honk_image = pygame.image.load('resources/HONK.png').convert_alpha()
        self.wood_image = pygame.image.load('resources/rpg_gui_v1/wood background.png').convert_alpha()
        self.ui_image = pygame.image.load('resources/rpg_gui_v1/RPG_GUI_v1.png').convert_alpha()
        self.dy = self.font.get_sized_height()
        rect = self.font.get_rect('M')
        self.dx = rect.width

        rect = self.font.get_rect(' ')
        self.space_width = rect.width

        self.max_width = self.max_columns * self.dx

        # HONK is too big at 282x282, so we're actually going to use it at 1/4
        # its original size.
        rect = self.honk_image.get_rect()
        rect.width //= 4
        rect.height //= 4
        self.honk_image = pygame.transform.scale(self.honk_image, (rect.width, rect.height))

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
        self.tl = self.ui_image.subsurface(rect)

        rect = pygame.Rect(893, 189, middle_width, corner_wh)
        self.tm = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 189, corner_wh, corner_wh)
        self.tr = self.ui_image.subsurface(rect)

        rect = pygame.Rect(856, 227, corner_wh, middle_height)
        self.ml = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 227, corner_wh, middle_height)
        self.mr = self.ui_image.subsurface(rect)

        rect = pygame.Rect(856, 294, corner_wh, corner_wh)
        self.bl = self.ui_image.subsurface(rect)

        rect = pygame.Rect(893, 294, middle_width, corner_wh)
        self.bm = self.ui_image.subsurface(rect)

        rect = pygame.Rect(978, 294, corner_wh, corner_wh)
        self.br = self.ui_image.subsurface(rect)

    def draw_ui(self, target):
        ''' Draw a UI around the text area. Co-ords are for the *internal*
        area, where text is going to be drawn by someone else.
        '''
        honk_rect = self.honk_image.get_rect()
        honk_x = target.x - self.margin - honk_rect.width
        honk_y = target.y - self.margin

        # Draw the background.
        rect = pygame.Rect(honk_x, honk_y, honk_rect.width + target.width, max(honk_rect.height, target.height))
        area = pygame.Rect(0, 0, rect.width, max(honk_rect.height, rect.height))
        self.screen.blit(self.wood_image, rect, area)

        # HONK!
        honk_rect.x = honk_x
        honk_rect.y = honk_y
        self.screen.blit(self.honk_image, honk_rect)

        # Draw some decoration.
        #
        # This is a bit gross, and the scaled subsurfaces should be created
        # one time, not every frame.
        corner_wh = 24
        middle_width = 73
        middle_height = 55

        w1 = corner_wh
        h1 = corner_wh
        w_scale = (target.w + honk_rect.width) / middle_width
        h_scale = target.h / middle_height

        rect = self.tm.get_rect()
        tm_scaled = pygame.transform.scale(self.tm, (int(rect.width * w_scale), rect.height))

        rect = self.ml.get_rect()
        ml_scaled = pygame.transform.scale(self.ml, (rect.width, int(rect.height * h_scale)))

        rect = self.mr.get_rect()
        mr_scaled = pygame.transform.scale(self.mr, (rect.width, int(rect.height * h_scale)))

        rect = self.bm.get_rect()
        bm_scaled = pygame.transform.scale(self.bm, (int(rect.width * w_scale), rect.height))

        tl_rect = pygame.Rect(target.x - w1 - honk_rect.width, target.y - h1,            corner_wh,    corner_wh)
        tm_rect = pygame.Rect(target.x - honk_rect.width,      target.y - h1,            middle_width, corner_wh)
        tr_rect = pygame.Rect(target.x + target.width,         target.y - h1,            corner_wh,    corner_wh)

        ml_rect = pygame.Rect(target.x - w1 - honk_rect.width, target.y,                 corner_wh,    middle_height)
        mr_rect = pygame.Rect(target.x + target.width,         target.y,                 corner_wh,    middle_height)

        bl_rect = pygame.Rect(target.x - w1 - honk_rect.width, target.y + target.height, corner_wh,    corner_wh)
        bm_rect = pygame.Rect(target.x - honk_rect.width,      target.y + target.height, middle_width, corner_wh)
        br_rect = pygame.Rect(target.x + target.width,         target.y + target.height, corner_wh,    corner_wh)

        rect = self.tl.get_rect()
        self.screen.blit(self.tl, tl_rect, rect)

        rect = tm_scaled.get_rect()
        self.screen.blit(tm_scaled, tm_rect, rect)

        rect = self.tr.get_rect()
        self.screen.blit(self.tr, tr_rect, rect)

        rect = ml_scaled.get_rect()
        self.screen.blit(ml_scaled, ml_rect, rect)

        rect = mr_scaled.get_rect()
        self.screen.blit(mr_scaled, mr_rect, rect)

        rect = self.bl.get_rect()
        self.screen.blit(self.bl, bl_rect, rect)

        rect = bm_scaled.get_rect()
        self.screen.blit(bm_scaled, bm_rect, rect)

        rect = self.br.get_rect()
        self.screen.blit(self.br, br_rect, rect)

    def draw(self):
        self.screen.fill(BLACK)

        self.font.render_to(self.screen, (10, 10), 'Press [Space] to add text.', WHITE)

        # Draw a rectangle around the text area so we can see if we go over.
        rect = pygame.Rect(self.text_x, self.text_y, self.max_columns * self.dx, self.max_lines * self.dy)
        self.draw_ui(rect)

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
