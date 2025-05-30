"""The base enemy class for moveable enemies to inherit from."""

import pygame
import engine
from .. import Moveable
from .. import Humanoid

# The enemy base class.
class EnemyBase(Moveable, Humanoid):
    # Construct a new enemy base.
    def __init__(self, eng, classname):
        # Call the moveable constructor and modify its default properties.
        Moveable.__init__(self, eng, classname)
        Humanoid.__init__(self)
        self.get_event("collisionfinal").hook(EnemyBase.player_collide)

        # Create new events for hitting the enemy from above and killing the enemy.
        self.set_event(engine.Event("player_hit", EnemyBase.player_hit)) # Called when player hits from above.
        self.set_event(engine.Event("kill", EnemyBase.kill))

        # Create some sound effects.
        self.kick = self._engine.create_sound("lostlevels/assets/audio/player/koopa_kick.ogg")
        self.stomp = self._engine.create_sound("lostlevels/assets/audio/player/enemy_stomp.ogg")
        self.kick.volume = 1
        self.stomp.volume = 1

        # Bind the level scene instance to this enemy.
        self.level = None

    # Handle collision with the player.
    def player_collide(self, name, returnValue, other, coltype, coldir):
        # If the other entity is not a player, continue.
        if other.get_class() != "player":
            return engine.Event.DETOUR_CONTINUE
        
        # If this enemy hit the player on the side, hurt the player.
        if coldir == engine.entity.COLDIR_LEFT or coldir == engine.entity.COLDIR_RIGHT:
            other.hurt()
            return engine.Event.DETOUR_CONTINUE
        
        # If the player hit this enemy from above, invoke the player_hit event.
        if engine.entity.is_collision_above(coltype, coldir):
            other.add_velocity_y = 400
            other.jump_multiplier = 1.2
            self.invoke_event("player_hit", other)
            return engine.Event.DETOUR_CONTINUE

        # Return?
        return engine.Event.DETOUR_CONTINUE
    
    # Handle being hit by the player from above.
    def player_hit(self, player):
        self.stomp.play()
        self.invoke_event("kill", True)

    # Handle killing this enemy.
    def kill(self, player_hit = False):
        self._engine.console.log(f"[Lost Levels]: enemy \"{self.get_class()}\" was killed")
        if not player_hit:
            self.kick.repeat()
        self._engine.delete_entity(self)
        self.level.get_save().header.m_uScore += 100
        self.alive = False