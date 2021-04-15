# Experiment 11 - Tilemap
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import os
import pygame
import pygame.freetype
import sys
import time

from xml.etree import ElementTree

SCREEN_TITLE = 'Experiment 11 - Tilemap'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


class Map:
    def __init__(self, map_path):
        tree = ElementTree.parse(map_path)
        self.root = tree.getroot()
        layers = self.root.findall('layer')
        if len(layers) > 1:
            raise SystemExit('Map has multiple layers, this experiment only deals with one.')

        # Tileset and image atlas paths are relative to the map file.
        prefix = os.path.split(map_path)[0]

        tileset = self.root.find('tileset')
        tileset_path = os.path.join(prefix, tileset.attrib['source'])
        tileset_tree = ElementTree.parse(tileset_path)
        tileset_root = tileset_tree.getroot()

        image = tileset_root.find('image')
        image_path = os.path.join(prefix, image.attrib['source'])
        self.texture = pygame.image.load(image_path).convert_alpha()
        texture_rect = self.texture.get_rect()

        # Map size in tiles.
        self.map_width = int(self.root.attrib['width'])
        self.map_height = int(self.root.attrib['height'])

        # Tile size in pixels.
        self.tile_width = int(tileset_root.attrib['tilewidth'])
        self.tile_height = int(tileset_root.attrib['tileheight'])

        # Create subsurfaces for the tiles in the atlas.
        self.tiles = [None]  # Index 0 means "don't draw a tile" in Tiled.
        for y in range(texture_rect.height // self.tile_height):
            for x in range(texture_rect.width // self.tile_width):
                tile_rect = pygame.Rect(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
                self.tiles.append(self.texture.subsurface(tile_rect))

        # Decode the layer data. This map is using CSV, which is easy; for
        # help decoding other formats, check out my tileset crusher's code:
        # https://github.com/Taffer/crushtileset/
        data = layers[0].find('data').text

        self.layer_data = []

        lines = data.split()
        for line in lines:
            for c in line.split(','):
                if c != '':
                    self.layer_data.append(int(c))

    def render(self, surface, view_rect):
        # TODO: How to batch this so it's faster?
        for y in range(view_rect.height):
            for x in range(view_rect.width):
                tile = self.tiles[self.layer_data[x + view_rect.x + (y + view_rect.y) * self.map_width + 1]]
                target = pygame.Rect(x * self.tile_width, y * self.tile_height, self.tile_width, self.tile_height)
                if tile is not None:
                    surface.blit(tile, target)


class Demo:
    def __init__(self, screen):
        self.screen = screen

        self.map = Map('resources/map.tmx')

        self.rect = screen.get_rect()
        self.view_rect = pygame.Rect(0, 0, self.rect.width // self.map.tile_width, self.rect.height // self.map.tile_height)

        self.font = pygame.freetype.Font('resources/fonts/LiberationSerif-Bold.ttf', 16)

    def draw(self):
        self.screen.fill(BLACK)
        self.map.render(self.screen, self.view_rect)
        self.font.render_to(self.screen, (10, 10), 'Press arrow keys or WASD.', WHITE)

    def update(self, dt):
        pass

    def view_left(self):
        # Move viewport left.
        self.view_rect.x -= 1
        if self.view_rect.x < 0:
            self.view_rect.x = 0

    def view_right(self):
        # Move viewport right.
        self.view_rect.x += 1
        if (self.view_rect.x + self.view_rect.width) > self.map.map_width:
            self.view_rect.x -= 1

    def view_up(self):
        # Move viewport up.
        self.view_rect.y -= 1
        if self.view_rect.y < 0:
            self.view_rect.y = 0

    def view_down(self):
        # Move viewport down.
        self.view_rect.y += 1
        if (self.view_rect.y + self.view_rect.height) > self.map.map_height:
            self.view_rect.y -= 1


def main():
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
                if event.key == pygame.K_ESCAPE:
                    sys.exit()
                elif event.key in (pygame.K_w, pygame.K_UP):
                    demo.view_up()
                elif event.key in (pygame.K_s, pygame.K_DOWN):
                    demo.view_down()
                elif event.key in (pygame.K_a, pygame.K_LEFT):
                    demo.view_left()
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    demo.view_right()


if __name__ == '__main__':
    main()
