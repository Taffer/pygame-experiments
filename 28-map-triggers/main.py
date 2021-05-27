# Experiment 26 - Ultima Tiles
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

SCREEN_TITLE = 'Experiment 26 - Smooth Tilemap'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
RED = pygame.Color('red')
WHITE = pygame.Color('white')


class Trigger:
    def __init__(self, on_enter, on_exit):
        ''' Trigger on a tile, calls on_enter/on_exit functions when moving.

        Design question: This could be implemented with callbacks like I've
        done here, or subclassing (then on_enter/on_exit are just the
        funcitons you implement). I'm not sure which one works better.
        '''
        self.enter_function = on_enter
        self.exit_function = on_exit

    def on_enter(self, x, y, actor):
        ''' Triggered when an actor enters this tile.
        '''
        if self.enter_function:
            self.enter_function(x, y, actor)

    def on_exit(self, x, y, actor):
        ''' Triggered when an actor exits this tile.
        '''
        if self.exit_function:
            self.exit_function(x, y, actor)


# Tiled map parser.
class Map:
    def __init__(self, map_path: str) -> None:
        self.on_enter_functions = []  # On map enter
        self.on_exit_functions = []  # On map exit
        self.triggers = {}  # Specific tile enter/exit.

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
                for c in data_contents.split(','):
                    this_data.append(int(c))
            elif data.attrib['encoding'] == 'base64' and data.attrib.get('compression', 'none') == 'zlib':
                the_data = base64.b64decode(data_contents)

                # CSV data is organized into rows, so we make this one big row.
                this_data = [x[0] for x in struct.iter_unpack('<I', zlib.decompress(the_data))]
            else:
                raise RuntimeError('Unsupported encoding/compression.')

            self.layer_data[layer.attrib['name']] = this_data

    def get_index(self, x: int, y: int) -> int:
        return x + y * self.map_width

    def get_tile(self, layer: str, x: int, y: int) -> int:
        idx = self.get_index(x, y)
        return self.layer_data[layer][idx]

    def get_tile_texture(self, idx: int) -> pygame.Surface:
        return self.tiles[idx]

    def add_onenter(self, on_enter):
        ''' Add an On Enter function to the map.

        On Enter functions are called with (x, y, actor) when an actor enters
        the map. (x, y) will be their spawn point in *tile* co-ordinates.

        Note that you can't remove On Enter functions.
        '''
        self.on_enter_functions.append(on_enter)

    def add_onexit(self, on_exit):
        ''' Add on On Exit function to the map.

        On Exit functions are called with (x, y, actor) when an actor exits
        the map. (x, y) will be their spawn point in *tile* co-ordinates.

        Note that you can't remove On Exit functions.
        '''
        self.on_exit_functions.append(on_exit)

    def add_trigger(self, x, y, on_enter, on_exit):
        ''' Add a trigger at (x,y).

        If you call this repeatedly with the same (x,y), it will overwrite the
        trigger. If you need to have multiple triggers on single tiles, use a
        pattern similar to the On Enter/On Exit lists instead of individual
        trigger objects.

        You can pass None for on_exit/on_exit if they're not needed.
        '''
        self.triggers[(x, y)] = Trigger(on_enter, on_exit)

    def enter_map(self, x, y, actor):
        for on_enter in self.on_enter_functions:
            on_enter(x, y, actor)

    def exit_map(self, x, y, actor):
        for on_exit in self.on_exit_functions:
            on_exit(x, y, actor)

    def enter_tile(self, x, y, actor):
        ''' *actor* has entered the tile at (x, y), activate any triggers.
        '''
        if (x, y) in self.triggers:
            self.triggers[(x, y)].on_enter(x, y, actor)

    def exit_tile(self, x, y, actor):
        ''' *actor* is exiting the tile at (x, y), activate any triggers.
        '''
        if (x, y) in self.triggers:
            self.triggers[(x, y)].on_exit(x, y, actor)


class Camera:
    ''' Camera/viewport for a tile-based map.
    '''
    def __init__(self: 'Camera', screen: pygame.Surface, the_map: Map) -> None:
        self.screen = screen
        self.map = the_map

        # Co-ordinates are in *tiles*, not pixels.
        self.x = 0
        self.y = 0
        self.tile_width = 0
        self.tile_height = 0

        # Co-ordinates are in *pixels*, not tiles.
        self.viewport = None

        # Tile to use for out-of-bounds tiles.
        self.edge_tile = 0

    def set_viewport(self: 'Camera', viewport: pygame.Rect) -> None:
        ''' Set the camera's on-screen viewport.
        '''
        self.viewport = viewport

        self.tile_width = viewport.width // self.map.tile_width
        self.tile_height = viewport.height // self.map.tile_height

    def set_position(self: 'Camera', x: int, y: int) -> None:
        self.x = x
        self.y = y

    def set_edge(self: 'Camera', edge: int) -> None:
        self.edge_tile = edge

    def get_rect(self: 'Camera') -> pygame.Rect:
        ''' Get the rectangle representing the camera position in screen pixels.
        '''
        return pygame.Rect(self.tile_width // 2 * self.map.tile_width, self.tile_height // 2 * self.map.tile_height,
                           self.map.tile_width, self.map.tile_height)

    def draw(self: 'Camera', layer: str) -> None:
        tile_x = self.x - self.tile_width // 2
        tile_y = self.y - self.tile_height // 2

        for y in range(self.tile_height):
            for x in range(self.tile_width):
                dx = tile_x + x
                dy = tile_y + y
                if dx < 0 or dx >= self.map.map_width or dy < 0 or dy >= self.map.map_height:
                    tile_idx = self.edge_tile
                else:
                    tile_idx = self.map.get_tile(layer, tile_x + x, tile_y + y)
                if tile_idx is not None:
                    tile = self.map.get_tile_texture(tile_idx)
                    target = pygame.Rect(self.viewport.x + x * self.map.tile_width, self.viewport.y + y * self.map.tile_height,
                                         self.map.tile_width, self.map.tile_height)
                    self.screen.blit(tile, target)


class Demo:
    def __init__(self: 'Demo', screen: pygame.Surface) -> None:
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)
        self.avatar = pygame.image.load('resources/031_avatar.png').convert_alpha()

        self.map = Map('resources/map.tmx')
        self.camera = Camera(self.screen, self.map)
        self.camera.set_position(self.map.map_width // 2, self.map.map_height // 2)

        # Viewport rect is in pixel coordinates.
        self.viewport = pygame.Rect(0, 0, 1280, 720)
        self.camera.set_viewport(self.viewport)
        self.camera.set_edge(30)  # "Deep water" from our tile set.

        # Set up some triggers.
        self.map.add_onenter(lambda x, y, actor: print('{0} entered the map at {1}, {2}'.format(actor, x, y)))
        self.map.add_onenter(lambda x, y, actor: print('Someone entered the map!'))

        self.map.add_trigger(24, 24, None, lambda x, y, actor: print('{0} is leaving {1}, {2}'.format(actor, x, y)))
        self.map.add_trigger(23, 24, lambda x, y, actor: print('{0} is entering {1}, {2}'.format(actor, x, y)), None)
        self.map.add_trigger(25, 24, lambda x, y, actor: print('{0} is entering {1}, {2}'.format(actor, x, y)), None)
        self.map.add_trigger(24, 23, lambda x, y, actor: print('{0} is entering {1}, {2}'.format(actor, x, y)), None)
        self.map.add_trigger(24, 25, lambda x, y, actor: print('{0} is entering {1}, {2}'.format(actor, x, y)), None)

        # There's a patch of tilled earth from (22, 12) to (27, 14). Don't walk
        # on my garden!
        for y in range(12, 15):
            for x in range(22, 28):
                self.map.add_trigger(x, y, lambda x, y, actor: print('GET OUT OF MY GARDEN, {0}!'.format(actor)), None)

        # Trigger enter triggers. The exit triggers won't ever be called in
        # this demo as we've only got one map.
        self.map.enter_map(self.camera.x, self.camera.y, 'Player Avatar')

        self.ticks = 0

        self.keystate = {
            pygame.K_w: False, pygame.K_UP: False,
            pygame.K_a: False, pygame.K_LEFT: False,
            pygame.K_s: False, pygame.K_DOWN: False,
            pygame.K_d: False, pygame.K_RIGHT: False,
        }

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        self.camera.draw('Tile Layer 1')

        rect = self.camera.get_rect()
        self.screen.blit(self.avatar, rect)

        self.font.render_to(self.screen, (10, 10), 'Use WASD or arrow keys to walk.', WHITE)

    def update(self: 'Demo', dt: float) -> None:
        self.ticks += dt
        if self.ticks > 1/20:
            self.ticks -= 1/20

            if self.keystate[pygame.K_w] or self.keystate[pygame.K_UP]:
                y = self.camera.y - 1

                if y >= 0:
                    tile = self.map.get_tile('Unwalkable', self.camera.x, y)
                    if tile == 0:
                        self.map.exit_tile(self.camera.x, self.camera.y, 'Player Avatar')
                        self.camera.set_position(self.camera.x, y)
                        self.map.enter_tile(self.camera.x, self.camera.y, 'Player Avatar')

            if self.keystate[pygame.K_s] or self.keystate[pygame.K_DOWN]:
                y = self.camera.y + 1
                if y < self.map.map_height:
                    tile = self.map.get_tile('Unwalkable', self.camera.x, y)
                    if tile == 0:
                        self.map.exit_tile(self.camera.x, self.camera.y, 'Player Avatar')
                        self.camera.set_position(self.camera.x, y)
                        self.map.enter_tile(self.camera.x, self.camera.y, 'Player Avatar')

            if self.keystate[pygame.K_a] or self.keystate[pygame.K_LEFT]:
                x = self.camera.x - 1

                if x >= 0:
                    tile = self.map.get_tile('Unwalkable', x, self.camera.y)
                    if tile == 0:
                        self.map.exit_tile(self.camera.x, self.camera.y, 'Player Avatar')
                        self.camera.set_position(x, self.camera.y)
                        self.map.enter_tile(self.camera.x, self.camera.y, 'Player Avatar')

            if self.keystate[pygame.K_d] or self.keystate[pygame.K_RIGHT]:
                x = self.camera.x + 1

                if x < self.map.map_width:
                    tile = self.map.get_tile('Unwalkable', x, self.camera.y)
                    if tile == 0:
                        self.map.exit_tile(self.camera.x, self.camera.y, 'Player Avatar')
                        self.camera.set_position(x, self.camera.y)
                        self.map.enter_tile(self.camera.x, self.camera.y, 'Player Avatar')


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
