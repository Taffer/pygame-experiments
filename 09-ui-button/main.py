# Experiment 9 - UI Button
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import time
import sys

SCREEN_TITLE = 'Experiment 9 - UI Button'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
WHITE = pygame.Color('white')


class Button:
    def __init__(self, x, y, text, font, button_normal, button_selected):
        rect = button_normal.get_rect()
        self.draw_rect = pygame.Rect(x, y, rect.width, rect.height)

        self.text = text
        self.button_normal = button_normal
        self.button_selected = button_selected

        self.font = font
        rect = self.font.get_rect(self.text)
        self.text_rect = pygame.Rect((self.draw_rect.width - rect.width) // 2,
                                     (self.draw_rect.height - rect.height) // 2,
                                     rect.width, rect.height)

        self.selected = False
        self.intersected = False

        self.on_click = None

    def draw(self, surface):
        if self.selected:
            surface.blit(self.button_selected, self.draw_rect)
        else:
            surface.blit(self.button_normal, self.draw_rect)

        rect = pygame.Rect(self.draw_rect.x + self.text_rect.x, self.draw_rect.y + self.text_rect.y,
                           self.text_rect.width, self.text_rect.height)
        self.font.render_to(surface, rect, self.text, WHITE)

        if self.intersected:
            pygame.gfxdraw.rectangle(surface, self.draw_rect, GREEN)

    def intersects(self, x, y):
        return self.draw_rect.collidepoint(x, y)

    def on_mouse_move(self, x, y):
        self.intersected = self.intersects(x, y)

    def on_mouse_press(self, x, y):
        if not self.intersects(x, y):
            return

        self.selected = True
        if self.on_click:
            self.on_click()

    def on_mouse_release(self, x, y):
        if not self.intersects(x, y):
            return

        self.selected = False


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.buff = []

        self.max_lines = 5
        self.max_columns = 20
        self.margin = 2

        self.text_x = 100
        self.text_y = 100

        self.font = pygame.freetype.Font('resources/fonts/LiberationSerif-Bold.ttf', 16)
        self.ui_image = pygame.image.load('resources/rpg_gui_v1/RPG_GUI_v1.png')

        rect = pygame.Rect(11, 124, 289, 59)
        self.button_normal = self.ui_image.subsurface(rect)
        rect = pygame.Rect(11, 202, 289, 59)
        self.button_selected = self.ui_image.subsurface(rect)

        # Let's make two buttons.
        self.ui = [
            Button(100, 100, 'Button 1', self.font, self.button_normal, self.button_selected),
            Button(250, 250, '# Two', self.font, self.button_normal, self.button_selected)
        ]

        self.ui[0].on_click = lambda: print('Mouse clicked on {0}'.format(self.ui[0].text))
        self.ui[1].on_click = lambda: print('Mouse clicked on {0}'.format(self.ui[1].text))

    def draw(self):
        self.screen.fill(BLACK)

        self.font.render_to(self.screen, (10, 10), 'Mouse over or click.', WHITE)

        for button in self.ui:
            button.draw(self.screen)

    def update(self, dt):
        pass

    def on_mouse_move(self, event):
        for button in self.ui:
            button.on_mouse_move(event.pos[0], event.pos[1])

    def on_mouse_release(self, event):
        for button in self.ui:
            button.on_mouse_release(event.pos[0], event.pos[1])

    def on_mouse_press(self, event):
        for button in self.ui:
            button.on_mouse_press(event.pos[0], event.pos[1])


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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False
            elif event.type == pygame.MOUSEMOTION:
                demo.on_mouse_move(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                demo.on_mouse_release(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                demo.on_mouse_press(event)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
