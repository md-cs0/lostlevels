"""Some funny boss I added for World 1-3."""

import pygame
import random
import math
import engine

from . import EnemyBase

# The Dr. House class.
class DrHouse(EnemyBase):
    # Construct a new Dr. House instance.
    def __init__(self, eng, classname):
         # Call the enemy base constructor and modify its default properties.
        super().__init__(eng, classname)
        self.speed = 0
        self.can_stomp = False

        # Load the Dr. House spritesheet.
        self.load("lostlevels/assets/sprites/dr_house.png", (86, 129), 1)

        # Start invoking the function responsible for handling Dr. House's moves.
        self._engine.create_timer(self.handle_actions, 0.5)

    # Handle Dr. House's moves.
    def handle_actions(self):
        # Exit if the entity has been deleted.
        if self.deleted:
            return
        
        # Choose what Dr. House should do next.
        if self.groundentity:
            choice = random.randint(1, 20)
            if 15 <= choice < 19:
                self.action_move()
            elif choice == 20:
                self.action_pounceattack()
                return

        # Call this function again 0.25s later.
        self._engine.create_timer(self.handle_actions, 0.25)

    # Jump around a bit.
    def action_move(self):
        self.velocity = pygame.math.Vector2(math.copysign(225, self.level.player.get_centre().x
                                                          - self.get_centre().x),
                                            300)
        
    # Pounce onto the player.
    def action_pounceattack(self):
        # Start the attack.
        self.movetype = engine.entity.MOVETYPE_CUSTOM
        self.velocity = pygame.math.Vector2((self.level.player.get_centre().x 
                                             - self.get_centre().x) * 3,
                                            900)
        self._engine.create_timer(self.action_fall, 1 / 3)

        # Make Dr. House scream.
        scream = self._engine.create_sound("lostlevels/assets/audio/objects/dr_house_screaming.ogg")
        scream.volume = 1
        scream.play()

    # After rising upwards, fall downwards.
    def action_fall(self):
        self.velocity = pygame.math.Vector2(0, -1000)
        self.get_event("collision").set_func(DrHouse.collision)

    # Handle collision wile falling.
    def collision(self, other, coltype, coldir):
        # If this entity is not hitting another entity, continue.
        if coltype != engine.entity.COLTYPE_COLLIDING:
            return

        # Delete the other entity.
        self._engine.delete_entity(other)                                            