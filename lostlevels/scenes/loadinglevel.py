"""A brief cutscene that occurs upon loading a level."""

"""The level selection scene for Lost Levels."""

import os
import pygame
import engine

from .. import levelinfo

# Loading level scene.
class LoadingLevel(engine.Game):
    # Construct the loading level scene.
    def __init__(self, eng, game):
        # Initialize the game interface.
        super().__init__(eng)
        self.__game = game

        # Declare the UI elements in advance.
        self.help = None
        self.input = None

        # Do we know which level to play?
        level = self.__game.save.currentlevel[self.__game.world - 1]
        if level <= levelinfo.NUM_LEVELS:
            self.__game.level = level
            self.load_level()
        else:
            # Seems like this world has already been completed. 
            # Instead, generate a prompt to the end-user where they
            # have to manually type in a level number instead.
            self.help = self._engine.create_ui_element_by_class("text")
            self.help.load_localfont("lostlevels/assets/fonts/nes.ttf")
            self.help.set_size(engine.ui.UDim2(0, 500, 0, 100))
            self.help.set_position(engine.ui.UDim2(0.5, -250, 0.5, -120))
            self.help.set_text(f"PLEASE TYPE A LEVEL NUMBER FROM 1-{levelinfo.NUM_LEVELS}")
            self.help.set_colour(pygame.Color(255, 255, 255))
            self.help.set_x_align(engine.ui.X_CENTRE)
            self.help.set_y_align(engine.ui.Y_BOTTOM)
            self.help.enabled = True

            # Create the actual textbox itself.
            self.input = self._engine.create_ui_element_by_class("text")
            self.input.load_localfont("lostlevels/assets/fonts/nes.ttf")
            self.input.set_size(engine.ui.UDim2(0, 500, 0, 20))
            self.input.set_position(engine.ui.UDim2(0.5, -250, 0.5, 20))
            self.input.set_text(f"1")
            self.input.set_colour(pygame.Color(255, 255, 255))
            self.input.set_x_align(engine.ui.X_CENTRE)
            self.input.set_y_align(engine.ui.Y_CENTRE)
            self.input.get_event("focuslost").set_func(lambda elem, enter_hit: self.levelselected())
            self.input.enabled = True
            self._engine.focus_text(self.input)

    # A level has been selected by the end-user.
    def levelselected(self):
        # Validate the level number selected.
        level = self.input.get_text().strip()
        if not level.isnumeric() or not (1 <= (level := int(level)) <= 2):
            self.help.set_text(f"THIS LEVEL NUMBER IS INVALID!\nPLEASE TYPE A LEVEL NUMBER FROM" \
                               f" 1-{levelinfo.NUM_LEVELS}")
            self._engine.create_timer(lambda: self._engine.focus_text(self.input), 0)
            return
        
        # Load the selected level.
        self.__game.level = level
        self.load_level()

    # Load the level module into the game and display a short
    # cutscene of the level that is about to begin.
    def load_level(self):
        # If the player selected a custom level, clear the current UI elements.
        self._engine.clear_foreground_elements()

        # If there exists any checkpoint data and there is a discrepancy between
        # the cached level number and the actual loaded level, wipe out the 
        # checkpoint data.
        if self.__game.checkpoint_level and self.__game.checkpoint_level != self.__game.level:
            self.__game.checkpoint_time_limit = None
            self.__game.checkpoint_player_offset = None
            self.__game.checkpoint_level = None

        # Verify the existence of the level module and load it.
        self._engine.console.log(f"[Lost Levels]: loading world {self.__game.world}-{self.__game.level}")
        path = f"lostlevels/worlds/{self.__game.world}/{self.__game.level}.py"
        if not os.path.isfile(path):
            self._engine.console.error(f"[Lost Levels]: missing module \"{path}\"!")
        self.__game.levelmodule = __import__(f"lostlevels.worlds.{self.__game.world}.{self.__game.level}", 
                                             fromlist = "*")
        
        # Create a textlabel for presenting the level to the player.
        worldname = self._engine.create_ui_element_by_class("text")
        worldname.load_localfont("lostlevels/assets/fonts/nes.ttf")
        worldname.set_size(engine.ui.UDim2(0, 150, 0, 20))
        worldname.set_position(engine.ui.UDim2(0.5, -75, 0.5, -50))
        worldname.set_text(f"WORLD {self.__game.world}-{self.__game.level}")
        worldname.set_colour(pygame.Color(255, 255, 255))
        worldname.set_x_align(engine.ui.X_CENTRE)
        worldname.enabled = True

        # Create an image of the player's head.
        player = self._engine.create_ui_element_by_class("image")
        player.load("lostlevels/assets/sprites/player_small.png")
        player.set_size(engine.ui.UDim2(0, 24, 0, 22), False)
        player.set_position(engine.ui.UDim2(0.5, -50, 0.5, -11))
        player.enabled = True
        
        # Create an "x" for the lives counter.
        x = self._engine.create_ui_element_by_class("text")
        x.load_localfont("lostlevels/assets/fonts/nes.ttf")
        x.set_size(engine.ui.UDim2(0, 12, 0, 12))
        x.set_position(engine.ui.UDim2(0.5, -6, 0.5, -6))
        x.set_text("X")
        x.set_colour(pygame.Color(255, 255, 255))
        x.set_x_align(engine.ui.X_CENTRE)
        x.enabled = True

        # Create a textlabel for the number of lives.
        lives = self._engine.create_ui_element_by_class("text")
        lives.load_localfont("lostlevels/assets/fonts/nes.ttf")
        lives.set_size(engine.ui.UDim2(0, 100, 0, 12))
        lives.set_position(engine.ui.UDim2(0.5, -53, 0.5, -6))
        lives.set_text(f"{self.__game.save.header.m_sLives}")
        lives.set_colour(pygame.Color(255, 255, 255))
        lives.set_x_align(engine.ui.X_RIGHT)
        lives.enabled = True

        # Create an image for the preview.
        preview = self._engine.create_ui_element_by_class("image")
        preview.load(self.__game.levelmodule.get_preview())
        preview.set_size(engine.ui.UDim2(0, 110, 0, 70))
        preview.set_position(engine.ui.UDim2(0.5, -55, 0.5, 39))
        preview.enabled = True

        # Keep this preview up for 2 seconds before we actually load the level.
        self._engine.create_timer(self.__game.load_level, 2)

    # Go back to the level selection map upon pressing ESC.
    def keydown(self, enum, unicode, focused):
        if enum == pygame.K_ESCAPE:
            self.__game.load_levelselection()