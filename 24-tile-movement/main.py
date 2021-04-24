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
        max_x = min(viewport.width, self.map_width)
        max_y = min(viewport.height, self.map_height)
        for y in range(max_y):
            for x in range(max_x):
                tile = self.tiles[self.layer_data[layer][self.get_index(x + viewport.x, y + viewport.y)]]
                target = pygame.Rect(offset_x + x * self.tile_width, offset_y + y * self.tile_height,
                                     self.tile_width, self.tile_height)
                if tile is not None:
                    surface.blit(tile, target)

    def get_index(self, x: int, y: int) -> int:
        return x + y * self.map_width

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

        self.feet_x = self.width // 2  # Where are the feet relative to 0,0?
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


class StateMachine:
    def __init__(self: 'StateMachine', initial_state: 'StateBase'):
        self.current = initial_state
        self.current.enter()

    def change(self: 'StateMachine', new_state: 'StateBase'):
        self.current.exit()
        self.current = new_state
        self.current.enter()

    def update(self: 'StateMachine', dt: float):
        next_state = self.current.update(dt)
        if next_state != self.current:
            self.change(next_state)


class StateBase:
    def __init__(self: 'StateBase', entity: 'Entity'):
        self.entity = entity
        self.ticks = 0

    def enter(self: 'StateBase'):
        pass

    def exit(self: 'StateBase'):
        pass

    def update(self: 'StateBase', dt: float):
        pass


class WaitState(StateBase):
    def __init__(self: 'WaitState', entity: 'Entity'):
        super().__init__(entity)

    def enter(self: 'WaitState'):
        self.entity.sprite.set_animation('idle')

    def exit(self: 'WaitState'):
        pass

    def update(self: 'WaitState', dt: float):
        walk = None
        self.ticks += dt

        if self.ticks > 0.1:
            self.ticks -= 0.1
            keystate = pygame.key.get_pressed()
            if keystate[pygame.K_w] or keystate[pygame.K_UP]:
                walk = {'x': 0, 'y': -1}  # go up
            elif keystate[pygame.K_s] or keystate[pygame.K_DOWN]:
                walk = {'x': 0, 'y': 1}  # go down
            elif keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
                walk = {'x': -1, 'y': 0}  # go left
            elif keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
                walk = {'x': 1, 'y': 0}  # go right

        if walk is not None:
            return WalkState(self.entity, walk)

        return self


class WalkState(StateBase):
    def __init__(self: 'WalkState', entity: 'Entity', direction: dict):
        super().__init__(entity)

        self.direction = direction

        self.target_x = self.entity.x
        self.target_y = self.entity.y

    def enter(self: 'WalkState'):
        self.entity.sprite.set_animation('walk')

        if self.direction['y'] == -1:  # go up
            self.entity.sprite.set_facing('away')
            self.target_y -= 1
        elif self.direction['y'] == 1:  # go down
            self.entity.sprite.set_facing('forward')
            self.target_y += 1
        elif self.direction['x'] == -1:  # go left
            self.entity.sprite.set_facing('left')
            self.target_x -= 1
        elif self.direction['x'] == 1:  # go right
            self.entity.sprite.set_facing('right')
            self.target_x += 1

        # Clamp movement to the map.
        if self.target_x < 0:
            self.target_x = 0
        elif self.target_x >= self.entity.map.map_width:
            self.target_x = self.entity.x
        if self.target_y < 0:
            self.target_y = 0
        elif self.target_y >= self.entity.map.map_height:
            self.target_y = self.entity.y

    def exit(self: 'WalkState'):
        pass

    def update(self: 'WalkState', dt: float):
        if self.target_x == self.entity.x and self.target_y == self.entity.y:
            return WaitState(self.entity)

        # TODO: needs tweening
        self.ticks += dt
        if self.ticks > 0.1:
            if self.direction['y'] == -1:  # go up
                self.entity.offset_y -= 1
            elif self.direction['y'] == 1:  # go down
                self.entity.offset_y += 1
            elif self.direction['x'] == -1:  # go left
                self.entity.offset_x -= 1
            elif self.direction['x'] == 1:  # go right
                self.entity.offset_x += 1

            self.entity.sprite.next_frame()

        if abs(self.entity.offset_x) >= self.entity.map.tile_width or \
           abs(self.entity.offset_y) >= self.entity.map.tile_height:  # Done moving.
            self.entity.teleport(self.target_x, self.target_y)
            return WaitState(self.entity)

        return self


class Entity:
    def __init__(self: 'Entity', sprite: LPCSprite, entity_map: Map):
        self.sprite = sprite
        self.map = entity_map
        self.x = 0
        self.y = 0

        self.offset_x = 0  # Drawing offsets for inter-tile animation.
        self.offset_y = 0

        self.controller = StateMachine(WaitState(self))

    def teleport(self: 'Entity', x: int, y: int):
        self.x = x
        self.y = y
        self.offset_x = 0
        self.offset_y = 0

    def draw(self: 'Entity', surface: pygame.Surface, x: int, y: int):
        # Draw sprite's feet at screen co-ords x, y.
        rect = pygame.Rect(x - self.sprite.width // 4, y - self.sprite.height // 2, self.sprite.width, self.sprite.height)
        rect.x += self.offset_x
        rect.y += self.offset_y
        surface.blit(self.sprite.get_texture(), rect)

    def draw_tile(self: 'Entity', surface: pygame.Surface, x: int, y: int, tile_width: int, tile_height: int):
        # Draw the tile the sprite thinks it's in.
        rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)
        pygame.gfxdraw.rectangle(surface, rect, RED)


class Demo:
    def __init__(self: 'Demo', screen: pygame.Surface) -> None:
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)

        self.sara_texture = pygame.image.load('resources/LPC_Sara/SaraFullSheet.png').convert_alpha()

        self.map = Map('resources/grass-map.tmx')
        # Viewport rect is in *tile* co-ordinates.
        self.viewport = pygame.Rect(0, 0, 1280 // self.map.tile_width, 720 // self.map.tile_height)

        self.sara = Entity(LPCSprite(self.sara_texture), self.map)
        self.sara.teleport(10, 10)  # Tile co-ordinates.

        self.ticks = 0

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        self.map.render('Tile Layer 1', self.screen, self.viewport, 0, 0)

        self.font.render_to(self.screen, (10, 10), 'Use WASD or arrow keys to walk.', WHITE)

        # Draw a rectangle to show which tile has the sprite's feet.
        self.sara.draw_tile(self.screen, self.sara.x, self.sara.y, self.map.tile_width, self.map.tile_height)

        # Draw Sara - We want her feet to be in the tile. This would be easier
        # if the sprite were the same size as our map tiles...
        self.sara.draw(self.screen, self.sara.x * self.map.tile_width, self.sara.y * self.map.tile_height)

    def update(self: 'Demo', dt: float) -> None:
        self.sara.controller.update(dt)


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
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    playing = False

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
