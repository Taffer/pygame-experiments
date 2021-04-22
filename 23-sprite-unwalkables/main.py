# Experiment 23 - Sprite Unwalkables
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import base64
import os
import pygame
import pygame.freetype
import pygame.gfxdraw
import struct
import sys
import time
import zlib

from xml.etree import ElementTree

SCREEN_TITLE = 'Experiment 23 - Sprite Unwalkables'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
RED = pygame.Color('red')
WHITE = pygame.Color('white')


# Tiled map parser.
class Map:
    def __init__(self, map_path: str) -> None:
        tree = ElementTree.parse(map_path)
        self.root = tree.getroot()
        layers = self.root.findall('layer')

        # Map size in tiles.
        self.map_width = int(self.root.attrib['width'])
        self.map_height = int(self.root.attrib['height'])

        # Tile size in pixels.
        self.tile_width = int(self.root.attrib['tilewidth'])
        self.tile_height = int(self.root.attrib['tileheight'])

        # Tileset and image atlas paths are relative to the map file.
        prefix = os.path.split(map_path)[0]

        tilesets = self.root.findall('tileset')
        self.tiles = [None]  # Index 0 means "don't draw a tile" in Tiled.
        for tileset in tilesets:
            tileset_path = os.path.join(prefix, tileset.attrib['source'])
            tileset_prefix = os.path.split(tileset_path)[0]
            tileset_tree = ElementTree.parse(tileset_path)
            tileset_root = tileset_tree.getroot()

            image = tileset_root.find('image')
            image_path = os.path.join(tileset_prefix, image.attrib['source'])
            texture = pygame.image.load(image_path).convert_alpha()
            texture_rect = texture.get_rect()

            # Create subsurfaces for the tiles in the atlas.
            for y in range(texture_rect.height // self.tile_height):
                for x in range(texture_rect.width // self.tile_width):
                    tile_rect = pygame.Rect(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
                    self.tiles.append(texture.subsurface(tile_rect))

        self.layer_data = {}
        for layer in layers:
            # Decode the layer data. This map is using CSV, which is easy; for
            # help decoding other formats, check out my tileset crusher's code:
            # https://github.com/Taffer/crushtileset/
            data = layer.find('data')
            data_contents = data.text

            this_data = []
            if data.attrib['encoding'] == 'csv':
                lines = data_contents.split()
                for line in lines:
                    for c in line.split(','):
                        if c != '':
                            this_data.append(int(c))
            elif data.attrib['encoding'] == 'base64' and data.attrib.get('compression', 'none') == 'zlib':
                the_data = base64.b64decode(data_contents)

                # CSV data is organized into rows, so we make this one big row.
                this_data = [x[0] for x in struct.iter_unpack('<I', zlib.decompress(the_data))]
            else:
                raise RuntimeError('Unsupported encoding/compression.')

            self.layer_data[layer.attrib['name']] = this_data

    def render(self, layer: str, surface: pygame.Surface, viewport: pygame.Rect, offset_x: int, offset_y: int) -> None:
        # This use case seems to be faster than using blits(); the overhead of
        # creating a list of tuples is probably what kills it.
        for y in range(viewport.height):
            for x in range(viewport.width):
                tile = self.tiles[self.layer_data[layer][self.get_index(x + viewport.x, y + viewport.y)]]
                target = pygame.Rect(offset_x + x * self.tile_width, offset_y + y * self.tile_height,
                                     self.tile_width, self.tile_height)
                if tile is not None:
                    surface.blit(tile, target)

    def get_index(self, x: int, y: int) -> int:
        return x + y * self.map_width + 1

    def get_tile(self, layer: str, x: int, y: int) -> int:
        return self.layer_data[layer][self.get_index(x, y)]


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

        self.sara_texture = pygame.image.load('resources/LPC_Sara/SaraFullSheet.png').convert_alpha()
        self.sara = LPCSprite(self.sara_texture)

        self.map = Map('resources/map.tmx')
        # Viewport rect is in *tile* co-ordinates.
        self.viewport = pygame.Rect(0, 0, 1280 // self.map.tile_width, 720 // self.map.tile_height)
        self.sara_x = 10 * self.map.tile_width  # 10,8 is on the beach in the top-left
        self.sara_y = 8 * self.map.tile_height

        self.ticks = 0

        self.keystate = {
            pygame.K_w: False, pygame.K_UP: False,
            pygame.K_a: False, pygame.K_LEFT: False,
            pygame.K_s: False, pygame.K_DOWN: False,
            pygame.K_d: False, pygame.K_RIGHT: False,
        }

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        self.map.render('Tile Layer 1', self.screen, self.viewport, 0, 0)

        self.font.render_to(self.screen, (10, 10), 'Use WASD or arrow keys to walk.', WHITE)

        # Draw a rectangle to show which tile has the sprite's feet.
        tile_w = self.map.tile_width
        tile_h = self.map.tile_height
        rect = pygame.Rect(((self.sara_x + self.sara.feet_x) // tile_w) * tile_w,
                           ((self.sara_y + self.sara.feet_y) // tile_h) * tile_h,
                           tile_w, tile_h)
        pygame.gfxdraw.rectangle(self.screen, rect, RED)

        # Draw Sara
        rect = pygame.Rect(self.sara_x, self.sara_y, self.sara.width, self.sara.height)
        self.screen.blit(self.sara.get_texture(), rect)

    def update(self: 'Demo', dt: float) -> None:
        tile_w = self.map.tile_width
        tile_h = self.map.tile_height
        current_rect = pygame.Rect(((self.sara_x + self.sara.feet_x) // tile_w) * tile_w,
                                   ((self.sara_y + self.sara.feet_y) // tile_h) * tile_h,
                                   tile_w, tile_h)

        go_up = self.keystate[pygame.K_w] or self.keystate[pygame.K_UP]
        go_left = self.keystate[pygame.K_a] or self.keystate[pygame.K_LEFT]
        go_down = self.keystate[pygame.K_s] or self.keystate[pygame.K_DOWN]
        go_right = self.keystate[pygame.K_d] or self.keystate[pygame.K_RIGHT]

        if not (go_up or go_left or go_down or go_right):
            self.sara.set_animation('idle')  # Default state is idling.

        orig_x = self.sara_x
        orig_y = self.sara_y

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

        # Clamp Sara's position and adjust the viewport, clumsily.
        if self.sara_x < 0:
            self.sara_x = 0 + 32
            self.viewport.x -= 1
        elif self.sara_x + self.sara.width > SCREEN_WIDTH:
            self.sara_x = SCREEN_WIDTH - self.sara.width - 32
            self.viewport.x += 1
        elif self.sara_y < 0:
            self.sara_y = 0 + 32
            self.viewport.y -= 1
        elif self.sara_y + self.sara.height > SCREEN_HEIGHT:
            self.sara_y = SCREEN_HEIGHT - self.sara.height - 32
            self.viewport.y += 1

        new_rect = pygame.Rect(((self.sara_x + self.sara.feet_x) // tile_w) * tile_w,
                               ((self.sara_y + self.sara.feet_y) // tile_h) * tile_h,
                               tile_w, tile_h)

        if current_rect != new_rect:
            tile_x = new_rect.x // tile_w + self.viewport.x
            tile_y = new_rect.y // tile_h + self.viewport.y
            if self.map.get_tile('Unwalkable', tile_x, tile_y):
                # Tile is blocked, cancel the move.
                self.sara_x = orig_x
                self.sara_y = orig_y

        self.ticks += dt
        if self.ticks > 1/12:  # 12 animation frames/second
            self.ticks -= 1/12
            self.sara.next_frame()


def main() -> None:
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
                demo.keystate[event.key] = True
            elif event.type == pygame.KEYUP:
                demo.keystate[event.key] = False
                if event.key == pygame.K_ESCAPE:
                    sys.exit()


if __name__ == '__main__':
    main()
