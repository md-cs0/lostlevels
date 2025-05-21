"""The level selection scene for Lost Levels."""

import pygame
import engine

from .. import levelinfo

# World portal.
class WorldPortal(engine.entity.Tile):
    # Construct the world portal entity.
    def __init__(self, engine, classname):
        # Call the tile constructor and add new properties.
        super().__init__(engine, classname)
        self.world = 0

# Level selection scene.
class LevelSelection(engine.Game):
    # Construct the level selection map.
    def __init__(self, eng, game):
        # Initialize the game interface.
        super().__init__(eng)
        self.__game = game
        self._engine.console.log("[Lost Levels]: launching level selection map")

        # Register WorldPortal as an engine entity type.
        self._engine.register_classname("worldportal", WorldPortal)

        # Create the background.
        self.room = self._engine.create_ui_element_by_class("image", engine.ui.LAYER_BACKGROUND)
        self.room.load("lostlevels/assets/biomes/levelselection/background.png")
        self.room.set_size(engine.ui.UDim2(1, 0, 1, 0))
        self.room.enabled = True

        # Load the level selection map music.
        self.music = self._engine.create_sound(
            "lostlevels/assets/audio/levelselection/sma4_world_e_castle.ogg")
        self.music.volume = 1
        self.music.play(True)

        # Create an invisible rectangle for the ground.
        self.ground = self._engine.create_entity_by_class("rect")
        self.ground.set_hitbox(pygame.math.Vector2(576, 65))
        self.ground.set_baseorigin(pygame.math.Vector2(0, -415))
        self.ground.draw = False
        self._engine.activate_entity(self.ground)

        # Create an invisible wall on the left-hand side of the map.
        self.leftwall = self._engine.create_entity_by_class("rect")
        self.leftwall.set_hitbox(pygame.math.Vector2(10, 480))
        self.leftwall.set_baseorigin(pygame.math.Vector2(-10, 0))
        self.leftwall.draw = False
        self._engine.activate_entity(self.leftwall)

        # Create an invisible wall on the right-hand side of the map.
        self.rightwall = self._engine.create_entity_by_class("rect")
        self.rightwall.set_hitbox(pygame.math.Vector2(10, 480))
        self.rightwall.set_baseorigin(pygame.math.Vector2(576, 0))
        self.rightwall.draw = False
        self._engine.activate_entity(self.rightwall)

        # Create the world portals.
        worlds = levelinfo.NUM_WORLDS
        if worlds > 0 and self.__game.save.currentlevel[0] == 1:
            worlds = 1
        for i in range(0, worlds):
            # Create the portal themselves.
            portal = self._engine.create_entity_by_class("worldportal")
            portal.movetype = engine.entity.MOVETYPE_NONE
            portal.load("lostlevels/assets/temp.png", (128, 128), i)
            portal.set_hitbox(pygame.math.Vector2(128, 200))
            portal.set_baseorigin(pygame.math.Vector2(32 + i * 192, -159))
            portal.world = i + 1
            portal.can_use = True
            portal.get_event("use").set_func(lambda elem: self.load_world(elem))
            self._engine.activate_entity(portal)

            # Create the sign shadow.
            shadow = self._engine.create_ui_element_by_class("frame", engine.ui.LAYER_BACKGROUND)
            shadow.set_size(engine.ui.UDim2(0, 100, 0, 20))
            shadow.set_position(engine.ui.UDim2(0, 48 + i * 192, 0, 327))
            shadow.enabled = True

            # Create the sign.
            sign = self._engine.create_ui_element_by_class("frame", engine.ui.LAYER_BACKGROUND)
            sign.set_size(engine.ui.UDim2(0, 100, 0, 20))
            sign.set_position(engine.ui.UDim2(0, 46 + i * 192, 0, 325))
            sign.set_colour(pygame.Color(255, 255, 255))
            sign.enabled = True

            # Create the text on the sign itself.
            text = self._engine.create_ui_element_by_class("text", engine.ui.LAYER_BACKGROUND)
            text.load_localfont("lostlevels/assets/fonts/nes.ttf")
            text.set_size(engine.ui.UDim2(0, 100, 0, 20))
            text.set_position(engine.ui.UDim2(0, 46 + i * 192, 0, 325))
            text.set_text(f"WORLD {i + 1}")
            text.set_x_align(engine.ui.X_CENTRE)
            text.set_y_align(engine.ui.Y_CENTRE)
            text.enabled = True

        # Create the player sprite.
        self.player = self._engine.create_entity_by_class("player")
        self.player.set_baseorigin(pygame.math.Vector2(50, -200))
        self.player.can_jump = False
        self._engine.activate_entity(self.player)

        # Create the USE key dialogue that moves with the player until the player
        # moves, before it eventually disappears.
        self.dialogue = self._engine.create_ui_element_by_class("text")
        self.dialogue.load_localfont("lostlevels/assets/fonts/nes.ttf", 9)
        self.dialogue.set_size(engine.ui.UDim2(0, 400, 0, 18))
        self.dialogue.set_text("PRESS THE USE KEY, E,\nTO ENTER A PORTAL!")
        self.dialogue.set_colour(pygame.Color(255, 255, 255))
        self.dialogue.enabled = True

    # Handle exiting back to the main menu and forward keydown events
    # to the player.
    def keydown(self, enum, unicode, focused):
        # Return to the main menu if the ESC key is pressed.
        if enum == pygame.K_ESCAPE:
            self.music.stop()
            self.__game.load_startmenu()

        # Forward this event to the player.
        self.player.keydown(enum, unicode, focused)

        # Disable the USE key dialogue.
        self.dialogue.enabled = False

    # Load a new world.
    def load_world(self, portal, started = False):
        # Return if the player is grounded.
        if not started and not self.player.groundentity:
            return

        # If the player just selected the USE key, show a jump "animation"
        # and call this method again half-a-second later to initiate the
        # world-loading sequence.
        if not started:
            self._engine.console.log(f"[Lost Levels]: loading world {portal.world}")
            self.player.jump_sound.play()
            self.player.moveable = False
            self.player.index = 4
            self.player.velocity.y = 650
            self.player.velocity.x = 0
            self.player.move = 0
            self._engine.create_timer(self.load_world, 0.5, portal, True)
        else:
            self.music.stop()
            self.__game.load_world(portal.world)

    # Move the USE key dialogue with the player.
    def post_physics(self):
        pos = self.player.get_baseorigin()
        self.dialogue.set_position(engine.ui.UDim2(0, pos.x + 30, 0, -pos.y))