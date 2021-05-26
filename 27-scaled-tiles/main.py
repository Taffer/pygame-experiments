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

SCREEN_TITLE = 'Experiment 27 - Scaled Tilemap'

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

        # Are we scaled?
        self.scale = 1
        self.scaled_tile_cache = {}
        self.scale_algo = None  # pygame.transform function for scaling

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

    def set_scale(self: 'Camera', scale: int, algorithm: any) -> None:
        ''' Set view scaling.

        A *scale* of 1 means no scaling, *algorithm* is ignored in that case.
        '''
        self.scale = scale
        self.scaled_tile_cache = {}  # Clear the cache if it's been used.
        self.scale_algo = algorithm

    def get_scaled_tile(self: 'Camera', tile_idx: int) -> pygame.Surface:
        if tile_idx in self.scaled_tile_cache:
            return self.scaled_tile_cache[tile_idx]

        tile = self.map.get_tile_texture(tile_idx)
        scaled_tile = None
        if self.scale_algo == pygame.transform.scale2x:
            scaled_tile = self.scale_algo(tile)
        else:
            rect = tile.get_rect()
            rect.width *= 2
            rect.height *= 2
            scaled_tile = self.scale_algo(tile, (rect.width, rect.height))
        self.scaled_tile_cache[tile_idx] = scaled_tile

        return scaled_tile

    def get_rect(self: 'Camera') -> pygame.Rect:
        ''' Get the rectangle representing the camera position in screen pixels.
        '''
        return pygame.Rect(self.tile_width // 2 * self.map.tile_width,
                           self.tile_height // 2 * self.map.tile_height,
                           self.map.tile_width * self.scale, self.map.tile_height * self.scale)

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
                    if self.scale == 1:
                        tile = self.map.get_tile_texture(tile_idx)
                        target = pygame.Rect(self.viewport.x + x * self.map.tile_width, self.viewport.y + y * self.map.tile_height,
                                             self.map.tile_width, self.map.tile_height)
                        self.screen.blit(tile, target)
                    elif self.scale == 2:
                        scaled_tile = self.get_scaled_tile(tile_idx)
                        scaled_target = pygame.Rect(self.viewport.x + x * self.map.tile_width * self.scale,
                                                    self.viewport.y + y * self.map.tile_height * self.scale,
                                                    self.map.tile_width * self.scale, self.map.tile_height * self.scale)
                        self.screen.blit(scaled_tile, scaled_target)
                    else:
                        raise RuntimeError('Only 1x and 2x are supported.')


class Demo:
    def __init__(self: 'Demo', screen: pygame.Surface) -> None:
        self.screen = screen

        self.font = pygame.freetype.Font('resources/LiberationMono-Bold.ttf', 16)
        self.avatar = pygame.image.load('resources/031_avatar.png').convert_alpha()
        rect = self.avatar.get_rect()
        rect.width *= 2
        rect.height *= 2
        self.avatar_scaled = pygame.transform.scale(self.avatar, (rect.width, rect.height))
        self.avatar_2x = pygame.transform.scale2x(self.avatar)
        self.avatar_smooth = pygame.transform.smoothscale(self.avatar, (rect.width, rect.height))

        self.map = Map('resources/map.tmx')
        self.camera = Camera(self.screen, self.map)
        self.camera.set_position(self.map.map_width // 2, self.map.map_height // 2)

        # Viewport rect is in pixel coordinates.
        self.viewport = pygame.Rect(0, 0, 1280, 720)
        self.camera.set_viewport(self.viewport)
        self.camera.set_edge(30)  # "Deep water" from our tile set.

        self.ticks = 0

        self.keystate = {
            pygame.K_w: False, pygame.K_UP: False,
            pygame.K_a: False, pygame.K_LEFT: False,
            pygame.K_s: False, pygame.K_DOWN: False,
            pygame.K_d: False, pygame.K_RIGHT: False,
        }

        self.scaling_mode = 0

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        self.camera.draw('Tile Layer 1')

        rect = self.camera.get_rect()
        if self.scaling_mode == 0:
            self.screen.blit(self.avatar, rect)
        elif self.scaling_mode == 1:
            self.screen.blit(self.avatar_scaled, rect)
        elif self.scaling_mode == 2:
            self.screen.blit(self.avatar_smooth, rect)
        elif self.scaling_mode == 3:
            self.screen.blit(self.avatar_2x, rect)

        self.font.render_to(self.screen, (10, 10), 'Use Space to switch scaling.', WHITE)
        if self.scaling_mode == 0:
            self.font.render_to(self.screen, (10, 30), 'Scaling: NONE', WHITE)
        elif self.scaling_mode == 1:
            self.font.render_to(self.screen, (10, 30), 'Scaling: Regular', WHITE)
        elif self.scaling_mode == 2:
            self.font.render_to(self.screen, (10, 30), 'Scaling: Smooth', WHITE)
        elif self.scaling_mode == 3:
            self.font.render_to(self.screen, (10, 30), 'Scaling: 2x', WHITE)

    def update(self: 'Demo', dt: float) -> None:
        pass


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
                elif event.key == pygame.K_SPACE:
                    demo.scaling_mode += 1

                    if demo.scaling_mode > 3:
                        demo.scaling_mode = 0

                    if demo.scaling_mode == 0:
                        demo.camera.set_scale(1, None)
                    elif demo.scaling_mode == 1:
                        demo.camera.set_scale(2, pygame.transform.scale)
                    elif demo.scaling_mode == 2:
                        demo.camera.set_scale(2, pygame.transform.smoothscale)
                    elif demo.scaling_mode == 3:
                        demo.camera.set_scale(2, pygame.transform.scale2x)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
