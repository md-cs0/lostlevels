"""A single-use rocket launcher that blows up half of the map, per approximate
estimates derived from my own imagination."""

import pygame
import engine
from . import MushroomBase

# The rocket launcher class.
class RocketLauncher(MushroomBase):
    # Construct a new rocket launcher power-up.
    def __init__(self, eng, classname):
        # Call the mushroom base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.get_event("pickup").set_func(RocketLauncher.pickup)
        self.get_event("per_frame").set_func(RocketLauncher.per_frame)
        self.set_event(engine.Event("fire", RocketLauncher.fire))
        self.speed = 0

        # Load the rocket launcher spritesheet.
        self.load("lostlevels/assets/sprites/rocket_launcher.png", (32, 14), 1)

        # Has this rocket launcher been equipped by a player?
        self.equipped = False

    # Pick up the rocket launcher.
    def pickup(self, player):
        self.powerup_sound.play()
        self.movetype = engine.entity.MOVETYPE_NONE
        self.equipped = player
        player.weapon = self
        return False

    # Move with the player if this rocket launcher has been equipped.
    def per_frame(self):
        if self.equipped:
            if abs(self.equipped.velocity.x) > 0.1:
                self.negate_speed = self.equipped.velocity.x < 0
                self.flip(self.negate_speed)
            self.set_baseorigin(self.equipped.get_baseorigin()
                + pygame.math.Vector2(-32 + self.equipped.get_hitbox().x if self.negate_speed else 0, 
                                      (-1 if 1 <= self.equipped.index <= 2 else 0) - 20))
            
    # Fire a rocket out of the rocket launcher and delete the rocket launcher.
    def fire(self):
        # Create a rocket manually.
        rocket = self._engine.create_entity_by_class("sprite")
        rocket.load("lostlevels/assets/sprites/rocket.png", (9, 4), 1)
        rocket.set_baseorigin((self.get_topleft() - pygame.math.Vector2(9, 0)) if self.negate_speed 
                              else (self.get_topright()) - pygame.math.Vector2(0, 2))
        rocket.flip(self.negate_speed)
        rocket.velocity.x = -2000 if self.negate_speed else 2000
        rocket.get_event("collisionfinal").set_func(rocket_hit)

        # Play a rocket shooting sound.
        shoot = self._engine.create_sound("lostlevels/assets/audio/objects/rocket_shoot.ogg")
        shoot.volume = 1
        shoot.play()

        # Delete this rocket launcher.
        self.equipped.weapon = None
        self._engine.delete_entity(self)
        
# Handle the rocket hitting other entities.
def rocket_hit(self, other, coltype, coldir):
    # Play an explosion sound.
    explosion = self._engine.create_sound("lostlevels/assets/audio/objects/rocket_hit.ogg")
    explosion.volume = 1
    explosion.play()

    # Create a flash bang that gradually fades.
    frame = self._engine.create_ui_element_by_class("frame")
    frame.set_size(engine.ui.UDim2(1, 0, 1, 0))
    frame.set_colour(pygame.Color(255, 255, 255, 255))
    frame.enabled = True
    self._engine.create_timer(fade_frame, 0.25, frame)

    # Query all entities within a large radius of the rocket and delete them.
    for ent in self._engine.query_entities_in_radius(self.get_centre(), 300):
        self._engine.delete_entity(ent)
    
    # Due to the previous code, this rocket entity should have been deleted already.

# Handle the gradual fading of the flash bang.
def fade_frame(self):
    colour = self.get_colour()
    if colour.a == 0:
        self._engine.delete_ui_element(self)
    else:
        self.set_colour(pygame.Color(255, 255, 255, max(0, colour.a - 3)))
        self._engine.create_timer(fade_frame, 1 / 20, self)
