-- Experiment 5 - Image Fades
--
-- By Chris Herborth (https://github.com/Taffer)
-- MIT license, see LICENSE.md for details.

-- All the stuff we've loaded already.
gameResources = {
    fonts = {},
    images = {}
}

-- Current state of the game.
gameState = {
    sprite_x = 100, -- Draw the normal sprite here.
    sprite_y = 100,

    sprite_dx = 150, -- Delta x for subsequent sprites.

    alpha = 0, -- Alpha channel for fades. 0 to 1 in 1 second.

    wait = 0,     -- wait 1 second, then start alpha over at 0
    wait_time = 1
}

-- Love callbacks.
function love.load()
    math.randomseed(os.time())
    love.graphics.setDefaultFilter('nearest', 'nearest')

    local gameResources = gameResources
    gameResources.images.robot = love.graphics.newImage('resources/character_robot_jump.png')
end

function love.draw()
    local gameResources = gameResources
    local gameState = gameState

    -- Background
    love.graphics.clear(0, 0, 0, 1)

    -- Normal sprite
    love.graphics.setColor(1, 1, 1, 1) -- White = "Draw images normally."
    love.graphics.draw(gameResources.images.robot, gameState.sprite_x, gameState.sprite_y)

    -- Linear fade.
    local sprite2_x = gameState.sprite_x + gameState.sprite_dx
    local sprite2_y = gameState.sprite_y
    love.graphics.setColor(1, 1, 1, gameState.alpha)
    love.graphics.draw(gameResources.images.robot, sprite2_x, sprite2_y)

    -- sin() fade
    sprite2_x = sprite2_x + gameState.sprite_dx
    local rads = gameState.alpha * (90 * math.pi / 180)
    love.graphics.setColor(1, 1, 1, math.sin(rads))
    love.graphics.draw(gameResources.images.robot, sprite2_x, sprite2_y)
end

function love.update(dt)
    local gameState = gameState

    -- Alpha += dt/2 means fade-in takes 2 seconds.
    gameState.alpha = gameState.alpha + dt / 2

    if gameState.alpha > 1 then
        gameState.alpha = 1

        gameState.wait = gameState.wait + dt
        if gameState.wait > gameState.wait_time then
            gameState.alpha = 0
            gameState.wait = 0
        end
    end
end

-- Event generation.
function love.keypressed(key)
    if key == 'escape' then
        love.event.quit()
    end
end
