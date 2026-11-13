"""A door sprite. This can either be for cosmetics, or it can actually
transport a player."""

import pygame
import engine

# The door class.
class Door(engine.entity.Sprite):
    # Construct a new pipe top.
    def __init__(self, eng, classname):
        # Call the sprite constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("use").set_func(Door.use)
        self.movetype = engine.entity.MOVETYPE_NONE

        # Load the door spritesheet.
        self.load("lostlevels/assets/sprites/smb2_door.png", (32, 64), 1)

        # Set some door-specific properties.
        self.level = None
        self.section = None
        self.offset = None
        self.entered = False
        self.door_open_sound = self._engine.create_sound("lostlevels/assets/audio/objects/door_open.ogg")
        self.door_open_sound.volume = 1

        # Create an event for door transportation.
        self.set_event(engine.Event("entered", Door.transport))

    # Transport the player to a given section.
    def transport(self):
        # Hide the door to create the impression it has been opened.
        self.draw = False
        
        # Create a 1.5-second timer for loading the next level section.
        self.level.player.can_die = False
        self._engine.delete_entity(self.level.player)
        self._engine.create_timer(self.load_newsection, 1.5)
        
    # Load the new section.
    def load_newsection(self):
        # Check that the pipe entity still exists.
        if self.deleted:
            return
        
        # Check that the player is stil alive.
        if not self.level.player.alive:
            return
        
        # Load the new level section.
        self.level.load_newlevel(self.section, self.offset, self.level.time_remaining)

    # Handle player transportation if the door is designed to do such.
    def use(self):
        # If this door has already been entered, return.
        if self.entered:
            return
        
        # Confirm whether this door is set up for transportation.
        if self.section == None:
            return
        
        # If the player has already started teleporting, return.
        if not self.level.player.can_die:
            return       

        # If the player is not grounded, return.
        if not self.level.player.groundentity:
            return 
        
        # Destroy the player entity and call the entered event,
        # while playing the door open sound.
        self.entered = True
        self.door_open_sound.play()
        self.invoke_event("entered")