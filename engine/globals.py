"""Global data for this engine, to be used by games."""

# Global variables struct for LLEngine.
class GlobalVars():
    def __init__(self):
        self.frametime = 0  # Delta time between previous and current frame (s).
        self.fps = 0        # The average FPS of the game. Calculations vary depending
                            # on which method of frame-limitation is used.
        self.frames = 0     # Number of frames ever since the engine launched.
        self.time = 0       # Time ever since the engine launched (s).