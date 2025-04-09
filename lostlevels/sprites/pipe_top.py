"""The top of a sprite. This can either be for cosmetics, or it can actually
transport a player."""

# Pipe orientation constants. These rotate clockwise.
PIPE_0      = 0
PIPE_90     = 1
PIPE_180    = 2
PIPE_270    = 3

import pygame
import engine

# The pipe top class.
class PipeTop(engine.entity.Tile):
    # Construct a new pipe top.
    def __init__(self, eng, classname):
        # Call the entity constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("collisionfinal").set_func(PipeTop.collisionfinal)

        # Set some pipe-specific properties.
        self.rotation = PIPE_0
        self.level = None
        self.section = None
        self.offset = None
        self.entered = False
        self.pipe_enter_sound = self._engine.create_sound("lostlevels/assets/audio/objects/pipe_enter.ogg")
        self.pipe_enter_sound.volume = 1

        # Create an event for pipe transportation.
        self.set_event(engine.Event("entered", PipeTop.transport))

    # Transport the player to a given section.
    def transport(self):
        # Create a 1.5-second timer for loading the next level section.
        self._engine.create_timer(self.level.load_newlevel, 1.5, 
                                  self.section, self.offset, self.level.time_remaining - 1.5)

    # Handle player transportation if the pipe is designed to do such.
    def collisionfinal(self, other, coltype, coldir):
        # If this pipe has already been entered, return.
        if self.entered:
            return
        
        # Confirm whether this pipe is set up for transportation.
        if self.section == None:
            return
        
        # Confirm whether the other entity is the player.
        if other != self.level.player:
            return
        
        # Confirm whether the player has actually attempted to walk into this pipe.
        keys = self._engine.get_keys_dict()
        if not ((coldir == engine.entity.COLDIR_UP and self.rotation == PIPE_0 and keys[pygame.K_DOWN])
                or (coldir == engine.entity.COLDIR_DOWN and self.rotation == PIPE_180)
                or (coldir == engine.entity.COLDIR_LEFT and self.rotation == PIPE_270 and keys[pygame.K_RIGHT])
                or (coldir == engine.entity.COLDIR_RIGHT and self.rotation == PIPE_90 and keys[pygame.K_LEFT])):
            return
        
        # Destroy the player entity and call the entered event,
        # while playing the pipe enter sound.
        self.pipe_enter_sound.play()
        self.level.player.can_die = False
        self._engine.delete_entity(other)
        self.invoke_event("entered")

# Define what should be imported from this module.
__all__ = ["PipeTop", "PIPE_0", "PIPE_90", "PIPE_180", "PIPE_270"]