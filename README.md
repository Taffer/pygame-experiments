# PyGame Experiments

Some experiments using the [PyGame](https://www.pygame.org/news) game framework
and Python.

These are ports of my
[Löve experiments](https://github.com/Taffer/love-experiments/) for now, we'll
see where this goes. Lua's easy enough and fast, but I'm happier developing in
Python…

Click through for more info:

* [01-scrolling-texture](01-scrolling-texture)
* [02-text-monospaced](02-text-monospaced)
* [03-text-variable](03-text-variable)
* [04-text-entry](04-text-entry)
* [05-image-fades](05-image-fades)
* [06-ui-dialog](06-ui-dialog)
* [07-animated-icon](07-animated-icon)
* [08-text-styled](08-text-styled)
* [09-ui-button](09-ui-button)
* [10-ui-spinbox](10-ui-spinbox)
* [11-tilemap](11-tilemap)
* [12-minimap-tilemap](12-minimap-tilemap)
* [13-rect-fades](13-rect-fades)
* [14-animated-sprite](14-animated-sprite)
* [15-text-dropshadow](15-text-dropshadow)
* [16-joystick](16-joystick)
* [17-sprite-joystick](17-sprite-joystick)
* [18-tilemap-layers](18-tilemap-layers)
* [19-simple-lighting](19-simple-lighting)
* [20-lpc-sprite](20-lpc-sprite)
* [21-blocked-sprite](21-blocked-sprite)
* [22-fancy-text](22-fancy-text)
* [23-sprite-unwalkables](23-sprite-unwalkables)
* [24-tile-movement](24-tile-movement)

## `pycodestyle`

Note that I use the following settings for `flake8` while working in
Sublime Text, your favourite editor or IDE might vary. Basically, doc comments
wrap at 80 characters, and the maximum line length is 132 characters (in homage
to þe olde terminals of yore):

```json
// SublimeLinter Settings - User
{
    // Linter settings.
    "linters": {
        "flake8": {
            "args": [
                "--max-line-length=132",
                "--max-doc-length=80"
            ]
        }
    }
}
```

## Bribe me

Want to bribe me to work on more experiments, faster? Want to suggest an
experiment?

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/U7U541Y8C)

Always willing to entertain suggestions, but if you're asking me to do some
work, you have the option of fuelling it with coffee. ;-)

## Credits

This is written in Python 3, using the [Pygame](https://www.pygame.org/) 2D
game engine.

## License

Stuff I wrote is released under the [MIT license](LICENSE.md), and any
resources are covered by their respective licenses (please see the `README.md`
files for details). I'm only using open source and freely usable third-party
bits, but they might not be using MIT's license.
