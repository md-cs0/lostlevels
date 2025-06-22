"""An interface for defining your own game."""

from . import main

# Use this interface to implement your game.
class Game():
    # Compose the engine with this game instance.
    def __init__(self, llengine):
        self._engine: main.LLEngine = llengine

    # Called when the engine is being started. This is a useful place to initialize
    # game variables that should otherwise be recognised by the engine's command
    # line parser.
    def init(self):
        pass

    # Called after the engine has started, just before the main game loop. Use this
    # for immediately rendering any UI elements/entities.
    def post_init(self):
        pass

    # Called each frame.
    def per_frame(self):
        pass

    # Called each frame after the physics engine has computed
    # its calculations.
    def post_physics(self):
        pass

    # Called when the engine concludes.
    def atexit(self, is_exception):
        pass

    # Called on KEYDOWN event.
    def keydown(self, enum, unicode, focused):
        pass

    # Called on KEYUP event.
    def keyup(self, enum, unicode, focused):
        pass