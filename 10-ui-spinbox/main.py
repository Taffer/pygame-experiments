# Experiment 10 - UI Spinbox
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import time
import sys

SCREEN_TITLE = 'Experiment 10 - UI Spinbox'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
GREEN = pygame.Color('green')
WHITE = pygame.Color('white')


class UIBase:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.on_click = None

    def intersects(self, x, y):
        return self.rect.collidepoint(x, y)

    def on_mouse_press(self, x, y):
        if not self.intersects(x, y):
            return  # Missed me!

        if self.on_click:
            self.on_click()


class ImageButton(UIBase):
    def __init__(self, x, y, surface):
        super().__init__()

        rect = surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = rect.width
        self.rect.height = rect.height

        self.surface = surface

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Label(UIBase):
    def __init__(self, x, y, text, font, surface):
        super().__init__()

        rect = surface.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rect.width = rect.width
        self.rect.height = rect.height

        self.text = text
        self.font = font
        self.surface = surface

        self.text_rect = pygame.Rect(0, 0, 0, 0)

        self.set_text(text)

    def set_text(self, text):
        self.text = text

        rect = self.font.get_rect(text)
        self.text_rect.width = rect.width
        self.text_rect.height = rect.height
        self.text_rect.x = (self.rect.width - rect.width) // 2  # Offset by x,y to draw
        self.text_rect.y = (self.rect.height - rect.height) // 2

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

        rect = pygame.Rect(self.text_rect)
        rect.x += self.rect.x
        rect.y += self.rect.y
        self.font.render_to(surface, rect, self.text, BLACK)


class Spinner(UIBase):
    def __init__(self, x, y, values, font, left_surface, label_surface, right_surface):
        super().__init__()

        self.rect.x = x
        self.rect.y = y

        self.values = values
        self.current_value = 0

        left_rect = left_surface.get_rect()
        label_rect = label_surface.get_rect()
        right_rect = right_surface.get_rect()

        self.decrease_button = ImageButton(x, y + (label_rect.height - left_rect.height) // 2, left_surface)
        self.decrease_button.on_click = self.decrease

        self.label = Label(x + left_rect.width, y, self.values[self.current_value], font, label_surface)

        self.increase_button = ImageButton(x + left_rect.width + label_rect.width, y + (label_rect.height - right_rect.height) // 2,
                                           right_surface)
        self.increase_button.on_click = self.increase

        self.rect.width = left_rect.width + label_rect.width + right_rect.width
        self.rect.height = max(left_rect.height, label_rect.height, right_rect.height)

    def decrease(self):
        self.current_value -= 1
        if self.current_value < 0:
            self.current_value = len(self.values) - 1
        self.label.set_text(self.values[self.current_value])

    def increase(self):
        self.current_value += 1
        if self.current_value >= len(self.values):
            self.current_value = 0
        self.label.set_text(self.values[self.current_value])

    def draw(self, screen):
        self.decrease_button.draw(screen)
        self.label.draw(screen)
        self.increase_button.draw(screen)

    def on_mouse_press(self, x, y):
        if not self.intersects(x, y):
            return

        self.decrease_button.on_mouse_press(x, y)
        self.increase_button.on_mouse_press(x, y)


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
        self.ui_image = pygame.image.load('resources/uipack/greenSheet.png')

        rect = pygame.Rect(378, 143, 39, 31)
        self.left_surface = self.ui_image.subsurface(rect)
        rect = pygame.Rect(339, 143, 39, 31)
        self.right_surface = self.ui_image.subsurface(rect)
        rect = pygame.Rect(0, 192, 190, 45)
        self.label_surface = self.ui_image.subsurface(rect)

        # Spinner!
        self.spinner = Spinner(100, 100, ['Value 1', 'Value Two', 'Three'], self.font, self.left_surface, self.label_surface,
                               self.right_surface)

    def draw(self):
        self.screen.fill(BLACK)

        self.font.render_to(self.screen, (10, 10), 'Click the buttons.', WHITE)

        self.spinner.draw(self.screen)

    def update(self, dt):
        pass

    def on_mouse_press(self, event):
        self.spinner.on_mouse_press(event.pos[0], event.pos[1])


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
            elif event.type == pygame.MOUSEBUTTONDOWN:
                demo.on_mouse_press(event)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
