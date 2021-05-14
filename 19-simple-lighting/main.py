# Experiment 19 - Simple Lights
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import math
import pygame
import pygame.freetype
import pygame.gfxdraw
import sys
import time

SCREEN_TITLE = 'Experiment 19 - Simple Lights'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
RED = pygame.Color('red')
WHITE = pygame.Color('white')

# LPC Sprite for animation.
#
# This sets up a set of sprites, quads, etc. using the standard Liberated
# Pixel Cup sprite format:
#
# https://lpc.opengameart.org/static/lpc-style-guide/styleguide.html
#
# Specifically:
# * Each row is a complete animation cycle.
# * Rows are mostly in groups of four based on facing = away, left, forward,
#   right.
# * Animation rows are: Spellcast, Thrust, Walk, Slash, Shoot, Hurt (only one
#   facing for Hurt). We fake an Idle animation by cloning the first frame of
#   Walk.
# * Are 64x64 on the sprite sheet.

# Note that this includes a non-standard animation, 'idle', made up of the
# first 'walk' frame.
LPC_ANIMATION = [
    'spellcast',
    'thrust',
    'walk',
    'slash',
    'shoot',
    'hurt',
    'idle'
]

LPC_FACING = [
    'away',
    'left',
    'forward',
    'right'
]

FRAMES = {
    LPC_ANIMATION[0]: 7,  # spellcast
    LPC_ANIMATION[1]: 8,  # thrust
    LPC_ANIMATION[2]: 9,  # walk
    LPC_ANIMATION[3]: 6,  # slash
    LPC_ANIMATION[4]: 13,  # shoot
    LPC_ANIMATION[5]: 6,  # hurt
    LPC_ANIMATION[6]: 1,  # idle
}


class LPCSprite:
    def __init__(self: 'LPCSprite', texture: pygame.Surface) -> None:
        self.width = 64
        self.height = 64

        self.feet_x = self.width / 2  # Where are the feet relative to 0,0?
        self.feet_y = self.height - 2

        self.facing = LPC_FACING[2]  # Default facing and animation.
        self.animation = LPC_ANIMATION[2]
        self.frame = 1

        self.texture = texture

        # Generate subsurfaces.
        self.frames = {}
        y = 0
        for av in LPC_ANIMATION[:-2]:  # "hurt" and "idle" are special cases
            self.frames[av] = {}

            for fv in LPC_FACING:
                self.frames[av][fv] = []
                for i in range(FRAMES[av]):
                    x = i * self.width
                    rect = pygame.Rect(x, y, self.width, self.height)
                    self.frames[av][fv].append(texture.subsurface(rect))

                y += self.height

        # "hurt" has to be special-cased because it only has one facing.
        self.frames['hurt'] = {}
        y = texture.get_height() - self.height
        for fv in LPC_FACING:
            # We'll use this animation for all four facings.
            self.frames['hurt'][fv] = []
        for i in range(FRAMES['hurt']):
            x = i * self.width
            rect = pygame.Rect(x, y, self.width, self.height)
            for fv in LPC_FACING:
                self.frames['hurt'][fv].append(texture.subsurface(rect))

        # "idle" is fake, just the first frame from "walk"
        self.frames['idle'] = {}
        for fv in LPC_FACING:
            self.frames['idle'][fv] = [self.frames['walk'][fv][0]]

    def check_frame(self: 'LPCSprite') -> None:
        if self.frame >= FRAMES[self.animation]:
            self.frame = 0

    def next_frame(self: 'LPCSprite') -> None:
        self.frame += 1
        self.check_frame()

    def set_facing(self: 'LPCSprite', facing: str) -> None:
        self.facing = facing
        self.check_frame()

    def set_animation(self: 'LPCSprite', animation: str) -> None:
        self.animation = animation
        self.check_frame()

    def get_texture(self: 'LPCSprite') -> pygame.Surface:
        return self.frames[self.animation][self.facing][self.frame]


class Demo:
    def __init__(self: 'Demo', screen: pygame.Surface) -> None:
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)

        self.grass = pygame.image.load('resources/grass.png').convert_alpha()
        self.grass_rect = self.grass.get_rect()
        self.sara_texture = pygame.image.load('resources/LPC_Sara/SaraFullSheet.png').convert_alpha()
        self.sara = LPCSprite(self.sara_texture)
        self.sara_x = 100
        self.sara_y = 100

        self.ticks = 0

        self.keystate = {
            pygame.K_w: False, pygame.K_UP: False,
            pygame.K_a: False, pygame.K_LEFT: False,
            pygame.K_s: False, pygame.K_DOWN: False,
            pygame.K_d: False, pygame.K_RIGHT: False,
        }

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        # Draw the grass.
        for y in range(0, SCREEN_HEIGHT, self.grass_rect.height):
            for x in range(0, SCREEN_WIDTH, self.grass_rect.width):
                rect = pygame.Rect(x, y, self.grass_rect.width, self.grass_rect.height)
                self.screen.blit(self.grass, rect)

        # Draw a rectangle to show which tile has the sprite's feet.
        tile_w = self.grass_rect.width
        tile_h = self.grass_rect.height
        rect = pygame.Rect(((self.sara_x + self.sara.feet_x) // tile_w) * tile_w,
                           ((self.sara_y + self.sara.feet_y) // tile_h) * tile_h,
                           tile_w, tile_h)
        pygame.gfxdraw.rectangle(self.screen, rect, RED)

        # Draw Sara
        rect = pygame.Rect(self.sara_x, self.sara_y, self.sara.width, self.sara.height)
        self.screen.blit(self.sara.get_texture(), rect)

        # Draw tile-based shadows centred on Sara's location. We use the middle
        # of her tile instead of her actual location for cleaner output.
        self.draw_shadows(self.sara_x + 16, self.sara_y + 16, 5, 128)

        self.shadow_text('Use WASD or arrow keys to walk.', 10, 10)

    def update(self: 'Demo', dt: float) -> None:
        go_up = self.keystate[pygame.K_w] or self.keystate[pygame.K_UP]
        go_left = self.keystate[pygame.K_a] or self.keystate[pygame.K_LEFT]
        go_down = self.keystate[pygame.K_s] or self.keystate[pygame.K_DOWN]
        go_right = self.keystate[pygame.K_d] or self.keystate[pygame.K_RIGHT]

        if not (go_up or go_left or go_down or go_right):
            self.sara.set_animation('idle')  # Default state is idling.

        if go_up:
            self.sara.set_facing('away')
            self.sara.set_animation('walk')

            self.sara_y = self.sara_y - 1
        elif go_down:
            self.sara.set_facing('forward')
            self.sara.set_animation('walk')

            self.sara_y = self.sara_y + 1
        elif go_left:
            self.sara.set_facing('left')
            self.sara.set_animation('walk')

            self.sara_x = self.sara_x - 1
        elif go_right:
            self.sara.set_facing('right')
            self.sara.set_animation('walk')

            self.sara_x = self.sara_x + 1

        # Clamp Sara's position.
        if self.sara_x < 0:
            self.sara_x = 0
        elif self.sara_x + self.sara.width > SCREEN_WIDTH:
            self.sara_x = SCREEN_WIDTH - self.sara.width
        elif self.sara_y < 0:
            self.sara_y = 0
        elif self.sara_y + self.sara.height > SCREEN_HEIGHT:
            self.sara_y = SCREEN_HEIGHT - self.sara.height

        self.ticks += dt
        if self.ticks > 1/12:  # 12 animation frames/second
            self.ticks -= 1/12
            self.sara.next_frame()

    def shadow_text(self, text, x, y):
        ''' Draw text with a drop-shadow at x,y.
        '''
        for dy in range(-1, 2, 2):
            for dx in range(-1, 2, 2):
                self.font.render_to(self.screen, (x + dx, y + dy), text, BLACK)
        self.font.render_to(self.screen, (x, y), text, WHITE)

    def draw_shadows(self, x, y, light_range, alpha):
        alpha_surface = pygame.Surface((32, 32))  # Size of a tile.
        alpha_surface.fill(BLACK)
        alpha_surface.set_alpha(alpha)

        screen_rect = self.screen.get_rect()
        for row in range(screen_rect.height // 32):
            for column in range(screen_rect.width // 32):
                centre_x = column * 32 + 16
                centre_y = row * 32 + 16

                dx = x - centre_x
                dy = y - centre_y

                distance = math.floor(math.sqrt(dx * dx + dy * dy) / 32)

                if distance > light_range:
                    # Draw a shadow.
                    dest = pygame.Rect(column * 32, row * 32, 32, 32)
                    self.screen.blit(alpha_surface, dest)


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
                demo.keystate[event.key] = True
            elif event.type == pygame.KEYUP:
                demo.keystate[event.key] = False
                if event.key == pygame.K_ESCAPE:
                    playing = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
