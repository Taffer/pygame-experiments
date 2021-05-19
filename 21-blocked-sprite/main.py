# Experiment 21 - Blocked Sprite
#
# By Chris Herborth (https://github.com/Taffer)
# MIT license, see LICENSE.md for details.

import pygame
import pygame.freetype
import pygame.gfxdraw
import random
import sys
import time

SCREEN_TITLE = 'Experiment 20 - LPC Sprite'

SCREEN_WIDTH = 1280  # 720p screen
SCREEN_HEIGHT = 720

BLACK = pygame.Color('black')
PURPLE = pygame.Color('purple')
RED = pygame.Color('red')
WHITE = pygame.Color('white')

TILE_SIZE = 32  # 32x32 tiles in use

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
        self.column = pygame.image.load('resources/col.png').convert_alpha()
        self.column_rect = self.column.get_rect()
        self.sara_texture = pygame.image.load('resources/LPC_Sara/SaraFullSheet.png').convert_alpha()
        self.sara = LPCSprite(self.sara_texture)
        self.sara_x = 100
        self.sara_y = 100
        self.sara_animation = 2
        self.sara.set_animation(LPC_ANIMATION[self.sara_animation])

        self.ticks = 0

        self.keystate = {
            pygame.K_w: False, pygame.K_UP: False,
            pygame.K_a: False, pygame.K_LEFT: False,
            pygame.K_s: False, pygame.K_DOWN: False,
            pygame.K_d: False, pygame.K_RIGHT: False,
        }

        self.blocks = []
        for i in range(10):
            block_x = random.randint(0, self.screen.get_width() // TILE_SIZE) * TILE_SIZE
            block_y = random.randint(0, self.screen.get_height() // TILE_SIZE) * TILE_SIZE
            self.blocks.append(pygame.Rect(block_x, block_y, TILE_SIZE, TILE_SIZE))

    def draw(self: 'Demo') -> None:
        self.screen.fill(BLACK)

        # Draw the grass.
        for y in range(0, SCREEN_HEIGHT, self.grass_rect.height):
            for x in range(0, SCREEN_WIDTH, self.grass_rect.width):
                rect = pygame.Rect(x, y, self.grass_rect.width, self.grass_rect.height)
                self.screen.blit(self.grass, rect)

        # Draw the blocks.
        for block in self.blocks:
            self.screen.blit(self.column, block)
            pygame.gfxdraw.rectangle(self.screen, block, PURPLE)

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

        self.shadow_text('Use WASD or arrow keys to walk.', 10, 10)

    def update(self: 'Demo', dt: float) -> None:
        go_up = self.keystate[pygame.K_w] or self.keystate[pygame.K_UP]
        go_left = self.keystate[pygame.K_a] or self.keystate[pygame.K_LEFT]
        go_down = self.keystate[pygame.K_s] or self.keystate[pygame.K_DOWN]
        go_right = self.keystate[pygame.K_d] or self.keystate[pygame.K_RIGHT]

        orig_x = self.sara_x
        orig_y = self.sara_y

        if not (go_up or go_down or go_left or go_right):
            self.sara.set_animation('idle')
        else:
            self.sara.set_animation('walk')

        if go_up:
            self.sara.set_facing('away')

            self.sara_y = self.sara_y - 1
        elif go_down:
            self.sara.set_facing('forward')

            self.sara_y = self.sara_y + 1

        if go_left:
            self.sara.set_facing('left')

            self.sara_x = self.sara_x - 1
        elif go_right:
            self.sara.set_facing('right')

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

        # Are there any blocks in the way?
        rect = pygame.Rect(((self.sara_x + self.sara.feet_x) // TILE_SIZE) * TILE_SIZE,
                           ((self.sara_y + self.sara.feet_y) // TILE_SIZE) * TILE_SIZE,
                           TILE_SIZE, TILE_SIZE)
        for block in self.blocks:
            if rect.x == block.x and rect.y == block.y:
                # Blocked!
                self.sara_x = orig_x
                self.sara_y = orig_y

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

'''
function love.update(dt)
    local gameState = gameState

    local gamepad_up = false
    local gamepad_down = false
    local gamepad_left = false
    local gamepad_right = false
    for _, joystick in ipairs(love.joystick.getJoysticks()) do
        if joystick:getName() == 'Xbox Wireless Controller' then
            -- That's the only one I have available, sorry. Expanding this is
            -- an exercise for the reader!
            --
            -- On the Xbox controller:
            --
            -- * 1 hat - gamepad
            -- * Axes 1, 2 - left stick left/right, up/down
            -- * Axes 4, 5 - right stick left/right, up/down
            local hat = joystick:getHat(1) -- 'c' means "centre"
            if hat == 'u' then
                gamepad_up = true
            elseif hat == 'lu' then
                gamepad_up = true
                gamepad_left = true
            elseif hat == 'ru' then
                gamepad_up = true
                gamepad_right = true
            elseif hat == 'l' then
                gamepad_left = true
            elseif hat == 'r' then
                gamepad_right = true
            elseif hat == 'd' then
                gamepad_down = true
            elseif hat == 'ld' then
                gamepad_down = true
                gamepad_left = true
            elseif hat == 'rd' then
                gamepad_down = true
                gamepad_right = true
            end

            local stickl_lr = joystick:getAxis(1)
            local stickl_ud = joystick:getAxis(2)
            local stickr_lr = joystick:getAxis(4)
            local stickr_ud = joystick:getAxis(5)

            if hat == 'u' or inRange(stickl_ud, -0.5, -1) or inRange(stickr_ud, -0.5, -1) then
                gamepad_up = true
            elseif hat == 'd' or inRange(stickl_ud, 1, 0.5) or inRange(stickr_ud, 1, 0.5) then
                gamepad_down = true
            end

            if hat == 'l' or inRange(stickl_lr, -0.5, -1) or inRange(stickr_lr, -0.5, -1) then
                gamepad_left = true
            elseif hat == 'r' or inRange(stickl_lr, 1, 0.5) or inRange(stickr_lr, 1, 0.5) then
                gamepad_right = true
            end
        end
    end

    local go_up = gameState.keys['w'] or gameState.keys['up'] or gamepad_up
    local go_left = gameState.keys['a'] or gameState.keys['left'] or gamepad_left
    local go_down = gameState.keys['s'] or gameState.keys['down'] or gamepad_down
    local go_right = gameState.keys['d'] or gameState.keys['right'] or gamepad_right

    if not (go_up or go_left or go_down or go_right) then
        gameState.sara:setState('idle') -- default state
    end

    local orig_x = gameState.sara_x
    local orig_y = gameState.sara_y

    if go_up then
        gameState.sara:setFacing('back')
        gameState.sara:setState('walk')

        gameState.sara_y = gameState.sara_y - 1
    end
    if go_down then
        gameState.sara:setFacing('front')
        gameState.sara:setState('walk')

        gameState.sara_y = gameState.sara_y + 1
    end
    if go_left then
        gameState.sara:setFacing('left')
        gameState.sara:setState('walk')

        gameState.sara_x = gameState.sara_x - 1
    end
    if go_right then
        gameState.sara:setFacing('right')
        gameState.sara:setState('walk')

        gameState.sara_x = gameState.sara_x + 1
    end

    -- Clamp Sara's position.
    if gameState.sara_x < 0 then
        gameState.sara_x = 0
    elseif gameState.sara_x + gameState.sara.width > gameState.screen_width then
        gameState.sara_x = gameState.screen_width - gameState.sara.width
    end
    if gameState.sara_y < 0 then
        gameState.sara_y = 0
    elseif gameState.sara_y + gameState.sara.height > gameState.screen_height then
        gameState.sara_y = gameState.screen_height - gameState.sara.height
    end

    gameState.sara:update(dt)
end
'''
