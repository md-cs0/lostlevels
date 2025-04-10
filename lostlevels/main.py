"""Lost Levels is a 2D-platformer inspired by Super Mario Bros.
and Syobon no Action, designed to infuriate players with obnoxious
yet humorous obstacles and game strategies which defy 2D-platformer
standards."""

import engine
import pygame
import numpy
import random 
import time
from . import scenes
from . import sprites

# Scene enums.
SCENE_NONE          = -1
SCENE_STARTMENU     = 0
SCENE_LEVELSELECT   = 1
SCENE_LOADINGLEVEL  = 2
SCENE_LEVEL         = 3

# Main game interface for Lost Levels.
class LostLevels(engine.Game):
    # Initialize the game interface.
    def __init__(self, llengine):
        # Initialize the game interface.
        super().__init__(llengine)

        # Define the current scene.
        self.__scene: engine.Game = None
        self.__sceneindex = -1

        # Store the save file here.
        self.save = None

        # Create a 1Hz 1s 4square wave.
        samples = (numpy.arange(engine.Sound.cached_sample_rate * 2) * numpy.pi 
                   / engine.Sound.cached_sample_rate)
        square = numpy.array([0] * engine.Sound.cached_sample_rate * 2).astype(numpy.int16)
        for i in range(1, 21, 2):
            square += (numpy.sin(samples * i) / i * 10000).astype(numpy.int16)

        # Create some new square wave channels for the intro music.
        self.__melody = self._engine.create_sound()
        self.__harmony1 = self._engine.create_sound()
        self.__harmony2 = self._engine.create_sound()
        self.__harmony2.volume = 0.35
        self.__bass = self._engine.create_sound()
        self.__bass.volume = 0.35
        self.__melody.buffer = self.__harmony1.buffer \
            = self.__harmony2.buffer = self.__bass.buffer = square

        # Set Python's RNG's seed to a hardcoded constant which can be changed later by
        # hitting keys, and play all the created square wave channels.
        random.seed(4389)
        self.__tweak_melody()
        self.__tweak_harmony1()
        self.__tweak_harmony2()
        self.__tweak_bass()

        # Register all of this game's entity types.
        self._engine.register_classname("player", sprites.Player)
        self._engine.register_classname("powerup_block", sprites.PowerupBlock)
        self._engine.register_classname("coin", sprites.Coin)
        self._engine.register_classname("pipetop", sprites.PipeTop)
        self._engine.register_classname("moveable", sprites.Moveable)
        self._engine.register_classname("mushroom_base", sprites.powerups.MushroomBase)
        self._engine.register_classname("glitch_powerup", sprites.powerups.GlitchPowerup)
        self._engine.register_classname("enemy_base", sprites.enemies.EnemyBase)
        self._engine.register_classname("goomba", sprites.enemies.Goomba)

        # Declare all the status bar's elements.
        self.scorebox = None
        self.livesbox = None
        self.coin = None
        self.coinsbox = None
        self.worldbox = None
        self.timebox = None

        # Store the current level information.
        self.world = 0
        self.level = 0
        self.levelmodule = None

    # Tweak the default width and height of this game to 576x480
    # and fix the game resolution to it. Furthermore, load the
    # start menu.
    def init(self):
        # Fix the resolution of the game.
        self._engine.width.set(self._engine.game_width.set(576))
        self._engine.height.set(self._engine.game_height.set(480))

        # Load the start menu.
        self.__sceneindex = SCENE_STARTMENU
        self.__scene = scenes.StartMenu(self._engine, self)

    # Forward all per-frame calls to the scene and manipulate the status
    # bar.
    def per_frame(self):
        # Forward per-frame calls to the scene.
        if self.__scene:
            self.__scene.per_frame()

        # If existent, modify the status bar.
        if self.scorebox:
            self.scorebox.set_text(f"FREEMAN\n{self.save.header.m_uScore:010d}")
        if self.coinsbox:
            self.coinsbox.set_text(f"x{self.save.header.m_sCoins}")
        if self.timebox and self.__sceneindex == SCENE_LEVEL:
            self.timebox.set_text(f"TIME\n{self.__scene.time_remaining:.0f}")

    # Forward all post-physics calls to the scene.
    def post_physics(self):
        if self.__scene:
            self.__scene.post_physics()

    # Forward all keydown events to the scene and change the random seed.
    def keydown(self, enum, unicode, focused):
        if self.__scene:
            self.__scene.keydown(enum, unicode, focused)
        random.seed(time.perf_counter_ns())

    # Forward all keyup events to the scene.
    def keyup(self, enum, unicode, focused):
        if self.__scene:
            self.__scene.keyup(enum, unicode, focused)

    # Upon exit, if a save file exists. save it.
    def atexit(self, is_exception):
        if self.save:
            self.save.write("saves")

    # Load the level selection map upon loading a new save.
    def load_levelselection(self):
        # Clear all UI elements.
        self._engine.clear_background_elements()
        self._engine.clear_foreground_elements()

        # Clear all entities.
        self._engine.clear_entities()

        # Stop playing the start menu music.
        if self.__melody != None:
            self.__melody.stop()
            self.__harmony1.stop()
            self.__harmony2.stop()
            self.__bass.stop()
            self.__melody = self.__harmony1 = self.__harmony2 = self.__bass = None

        # Change the scene to the level selection map scene.
        self.__sceneindex = SCENE_LEVELSELECT
        self.__scene = scenes.LevelSelection(self._engine, self)

        # Load the status bar.
        self.create_statusbar()

    # Load the start menu.
    def load_startmenu(self):
        # Clear all UI elements.
        self._engine.clear_background_elements()
        self._engine.clear_foreground_elements()

        # Clear all entities.
        self._engine.clear_entities()

        # Load the start menu.
        self.__sceneindex = SCENE_STARTMENU
        self.__scene = scenes.StartMenu(self._engine, self)

    # Load a new world.
    def load_world(self, world):
        # Clear all UI elements.
        self._engine.clear_background_elements()
        self._engine.clear_foreground_elements()

        # Clear all entities.
        self._engine.clear_entities()

        # Set the new world.
        self.world = world

        # Load the next level.
        self.__sceneindex = SCENE_LOADINGLEVEL
        self.__scene = scenes.LoadingLevel(self._engine, self)
    
    # Load a section of the level.
    def load_level(self, section = "main", offset = None, time_remaining = 200):
        # Clear all UI elements.
        self._engine.clear_background_elements()
        self._engine.clear_foreground_elements()

        # Clear all entities.
        self._engine.clear_entities()

        # Load the status bar.
        self.create_statusbar()
        self.worldbox.set_text(f"WORLD\n{self.world}-{self.level}")
        
        # Create the level scene and stop the music of the previous level scene,
        # if there is currently one already.
        if self.__sceneindex == SCENE_LEVEL:
            self.__scene.stop_music()
        self.__sceneindex = SCENE_LEVEL
        self.__scene = scenes.Level(self._engine, self, section, offset, time_remaining)

    # Create the status bar.
    def create_statusbar(self):
        # Create the score textbox.
        self.scorebox = self._engine.create_ui_element_by_class("text")
        self.scorebox.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.scorebox.set_size(engine.ui.UDim2(0, 200, 0, 100))
        self.scorebox.set_position(engine.ui.UDim2(0, 25, 0, 25))
        self.scorebox.set_text("FREEMAN\n0000000000")
        self.scorebox.set_colour(pygame.Color(255, 255, 255))
        self.scorebox.enabled = True

        # Create the coins textbox.
        self.coinsbox = self._engine.create_ui_element_by_class("text")
        self.coinsbox.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.coinsbox.set_size(engine.ui.UDim2(0, 75, 0, 100))
        self.coinsbox.set_position(engine.ui.UDim2(0.5, -100, 0, 37))
        self.coinsbox.set_text("x00")
        self.coinsbox.set_colour(pygame.Color(255, 255, 255))
        self.coinsbox.enabled = True

        # Create the coin to accompany the coins textbox.
        self.coin = self._engine.create_ui_element_by_class("image")
        self.coin.load("lostlevels/assets/biomes/levelselection/coin.png")
        self.coin.set_size(engine.ui.UDim2(0, 6, 0, 11))
        self.coin.set_position(engine.ui.UDim2(0.5, -110, 0, 37))
        self.coin.enabled = True

        # Create the lives textbox.
        self.livesbox = self._engine.create_ui_element_by_class("text")
        self.livesbox.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.livesbox.set_size(engine.ui.UDim2(0, 75, 0, 100))
        self.livesbox.set_position(engine.ui.UDim2(0.5, -38, 0, 25))
        self.livesbox.set_text(f"LIVES\n{self.save.header.m_sLives}")
        self.livesbox.set_colour(pygame.Color(255, 255, 255))
        self.livesbox.set_x_align(engine.ui.X_CENTRE)
        self.livesbox.enabled = True

        # Create the world textbox.
        self.worldbox = self._engine.create_ui_element_by_class("text")
        self.worldbox.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.worldbox.set_size(engine.ui.UDim2(0, 75, 0, 100))
        self.worldbox.set_position(engine.ui.UDim2(0.5, 84, 0, 25))
        self.worldbox.set_text("WORLD\nSELECT")
        self.worldbox.set_colour(pygame.Color(255, 255, 255))
        self.worldbox.set_x_align(engine.ui.X_CENTRE)
        self.worldbox.enabled = True

        # Create the time textbox.
        self.timebox = self._engine.create_ui_element_by_class("text")
        self.timebox.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.timebox.set_size(engine.ui.UDim2(0, 75, 0, 100))
        self.timebox.set_position(engine.ui.UDim2(1, -86, 0, 25))
        self.timebox.set_text("TIME")
        self.timebox.set_colour(pygame.Color(255, 255, 255))
        self.timebox.set_x_align(engine.ui.X_CENTRE)
        self.timebox.enabled = True

    # Tweak the melody channel's pitch.
    def __tweak_melody(self):
        if self.__melody != None:
            self.__melody.speed = random.randint(700, 900)
            self.__melody.repeat(True)
            self._engine.create_timer(self.__tweak_melody, 0.165)

    # Tweak the bass channel's pitch.
    def __tweak_harmony1(self):
        if self.__harmony1 != None:
            self.__harmony1.speed = self.__melody.speed / 2
            self.__harmony1.repeat(True)
            self._engine.create_timer(self.__tweak_harmony1, 0.165)

    # Tweak the bass channel's pitch.
    def __tweak_harmony2(self):
        if self.__harmony2 != None:
            self.__harmony2.speed = random.randint(1600, 2400)
            self.__harmony2.stop()
            if random.randint(1, 5) == 1:
                self.__harmony2.play(True)
            self._engine.create_timer(self.__tweak_harmony2, 0.165)

    # Tweak the bass channel's pitch.
    def __tweak_bass(self):
        if self.__bass != None:
            self.__bass.speed = random.randint(150, 375)
            self.__bass.repeat(True)
            self._engine.create_timer(self.__tweak_bass, 0.33)