# Experiment 8 - Styled Text

This is an attempt to create a simple text window that supports some text
styling (multiple fonts and colours). Print text to it, render it, and scroll
up when you reach the bottom.

![Experiment 8 - Styled Text](experiment-8.png)

You can run it from this directory with:

```sh
python3 main.py
```

or:

```sh
python main.py
```

If you're using Sublime Text:

1. Open the project.
1. Under Tools -> Build System, choose "Pygame - Main". You only need to pick
   the build system once, it's stored in the workspace file.
1. Choose Tools -> Build or press its shortcut (Ctrl+B).

Press Escape to exit the demo.

## Credits

This is written in Python 3, using the [PyGame](https://www.pygame.org/news) 2D
game engine.

### Graphics

* `LiberationMono-Bold.ttf` and `LiberationSerif-Bold.ttf` - Open source fonts
  from the
  [liberationfonts](https://github.com/liberationfonts/liberation-fonts) repo;
  this is licensed under the
  [SIL Open Font License](https://github.com/liberationfonts/liberation-fonts/blob/master/LICENSE).

### Libraries

* [middleclass](https://github.com/kikito/middleclass) by Enrique García Cota
