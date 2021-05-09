# Experiment 13 - Rect Fades
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.gfxdraw
import time
import sys

SCREEN_TITLE = 'Experiment 13 - Rect Fades'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.alpha = 0
        self.fade_out = True

        self.foxgirl = pygame.image.load('resources/fox n girl shadows.png').convert_alpha()
        self.foxgirl_rect = self.foxgirl.get_rect()

        self.alpha_surface = pygame.Surface((self.foxgirl_rect.width, self.foxgirl_rect.height))
        self.alpha_surface.fill(BLACK)
        self.alpha_surface.set_alpha(self.alpha)

    def draw(self):
        self.screen.fill(BLACK)
        self.screen.blit(self.foxgirl, self.foxgirl_rect)

        self.alpha_surface.set_alpha(int(self.alpha))
        self.screen.blit(self.alpha_surface, self.foxgirl_rect)

    def update(self, dt):
        if self.fade_out:
            self.alpha += dt * 120
            if self.alpha > 255:
                self.alpha = 255
                self.fade_out = False
        else:
            self.alpha -= dt * 120
            if self.alpha < 0:
                self.alpha = 0
                self.fade_out = True


def main():
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
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
