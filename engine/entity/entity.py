"""The root entity class, which Tile and Sprite are derived from.

These are the moving objects in a game, using this engine."""

import pygame
from ..event import Event
from .physics import CELL_SIZE

# Move types.
MOVETYPE_NONE       = 0 # This entity is not recognised by the physics engine.
MOVETYPE_ANCHORED   = 1 # This entity is recognised by the physics engine, but will not move. 
                        # Collision is possible.
MOVETYPE_PHYSICS    = 2 # This entity will be manipulated by the physics engine.
MOVETYPE_CUSTOM     = 3 # Custom physics is written for this entity.

# The root entity class.
class Entity():
    # Construct a new entity.
    def __init__(self, engine, classname = "entity"):
        # Set some basic identifiable attributes for this entity.
        self.__classname = classname
        self.__events = dict()
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._engine = engine
        self.active = False
        self.draw = True
        self.can_use = False

        # Entity motion.
        self.velocity = pygame.math.Vector2()       # The entity velocity as described by itself.
        self.__baseorigin = pygame.math.Vector2()   # The entity position as described by itself.
        self.__origindisp = pygame.math.Vector2()   # Displacement to add onto the base origin.
        self.__hitbox = pygame.math.Vector2()       # The size of the hitbox of the entity.

        # Physics engine properties.
        self.groundentity = None                    # The entity that this entity is grounded on.
        self.movetype = MOVETYPE_NONE               # The default movetype of this entity.
        self.move = 0.00                            # Scalar quantity representing horizontal movement, bound to friction.
        self.friction = 1.00                        # Friction multiplier.
        self.acceleration = 4.5                     # Acceleration multiplier.
        self.dirty = False                          # Has the origin of the entity changed?

        # Create a few crucial events.
        self.set_event(Event("draw", placeholder))
        self.set_event(Event("activated", lambda self: None))
        self.set_event(Event("per_frame", lambda self: None))
        self.set_event(Event("collision", lambda self, other, coltype, coldir: True))
        self.set_event(Event("collisionfinal", lambda self, other, coltype, coldir: None))
        self.set_event(Event("use", lambda self: None))

        # Engine linked list implementation.
        self.prev = None
        self.next = None
        self.deleted = False # Set to True after this entity is unlinked.

        # Reference hashes for the scene grid.
        self.gridhashes = None
        self.drawgrid = False

    # Get the class name of this entity.
    def get_class(self):
        return self.__classname
    
    # Get the absolute origin of this entity.
    def get_absorigin(self):
        return self.__baseorigin + self.__origindisp
    
    # Get the top-left absolute origin of this entity.
    def get_abstopleft(self):
        return pygame.math.Vector2(self._rect.left, -self._rect.top)
    
    # Get the top-right absolute origin of this entity.
    def get_abstopright(self):
        return pygame.math.Vector2(self._rect.right, -self._rect.top)
    
    # Get the bottom-left absolute origin of this entity.
    def get_absbottomleft(self):
        return pygame.math.Vector2(self._rect.left, -self._rect.bottom)
    
    # Get the bottom-right absolute origin of this entity.
    def get_absbottomright(self):
        return pygame.math.Vector2(self._rect.right, -self._rect.bottom)
    
    # Get the centre absolute origin of this entity.
    def get_abscentre(self):
        return pygame.math.Vector2(self._rect.left + self._rect.width // 2, 
                                   -self._rect.bottom - self._rect.height // 2)
    
    # Get the top-left base origin of this entity.
    def get_topleft(self):
        return self.get_baseorigin()
    
    # Get the top-right base origin of this entity.
    def get_topright(self):
        origin = self.get_baseorigin()
        return pygame.math.Vector2(origin.x + self.__hitbox.x,
                                   origin.y)
    
    # Get the bottom-left base origin of this entity.
    def get_bottomleft(self):
        origin = self.get_baseorigin()
        return pygame.math.Vector2(origin.x,
                                   origin.y - self.__hitbox.y)
    
    # Get the bottom-right base origin of this entity.
    def get_bottomright(self):
        origin = self.get_baseorigin()
        return pygame.math.Vector2(origin.x + self.__hitbox.x,
                                   origin.y - self.__hitbox.y)
    
    # Get the centre absolute origin of this entity.
    def get_centre(self):
        origin = self.get_baseorigin()
        return pygame.math.Vector2(origin.x + self.__hitbox.x / 2,
                                   origin.y - self.__hitbox.y / 2)
    
    # Get the absolute origin of the entity as window co-ordinates.
    def get_absorigin_coord(self):
        origin = self.get_absorigin()
        return (origin.x, -origin.y)

    # Get the base origin of this entity.
    def get_baseorigin(self):
        return self.__baseorigin
    
    # Set the base origin of this entity.
    def set_baseorigin(self, vec):
        if vec != self.__baseorigin:
            self.dirty = True
        self.__baseorigin = vec
        absorigin = self.get_absorigin()
        self._rect.left = absorigin.x
        self._rect.top = -absorigin.y

    # Get the origin displacement of this entity.
    def get_origindisp(self):
        return self.__origindisp
    
    # Set the origin displacement of this entity.
    def set_origindisp(self, vec):
        self.__origindisp = vec
        absorigin = self.get_absorigin()
        self._rect.left = absorigin.x
        self._rect.top = -absorigin.y

    # Get the base velocity of this entity.
    def get_basevelocity(self):
        return self.__basevelocity
    
    # Set the base velocity of this entity.
    def set_basevelocity(self, vec):
        self.__basevelocity = vec

    # Get the hitbox of this entity.
    def get_hitbox(self):
        return self.__hitbox

    # Set the hitbox of this entity.
    def set_hitbox(self, vec):
        self.__hitbox = vec
        self._rect.w = vec.x
        self._rect.h = vec.y
    
    # Check if this entity collides with another entity on the x axis.
    def collides_x(self, other):
        return (self._rect.left < other._rect.right 
                and self._rect.right > other._rect.left)
    
    # Check if this entity collides with another entity on the y axis.
    def collides_y(self, other):
        return (self._rect.top < other._rect.bottom
                and self._rect.bottom > other._rect.top)
    
    # Check if this entity collides with another entity (AABB).
    def collides(self, other):
        return self._rect.colliderect(other._rect)

    # Retrieve an event from this entity.
    def get_event(self, name):
        if name not in self.__events:
            self._engine.console.warn(f"Entity {self.__classname}: could not find event \"{name}\"")
            return None
        return self.__events[name]

    # Set an event to this entity.
    def set_event(self, event):
        self.__events[event.get_name()] = event

    # Invoke an event.
    def invoke_event(self, name, *args):
        if (event := self.get_event(name)) == None:
            return None
        return event.invoke(self, *args)

    # Handle entity deletion by unlinking this entity from its neighbouring entities.
    def unlink(self):
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev

    # Draw all the grid cells this entity is in for debugging purposes.
    def draw_grid(self, background):
        # Walk through each grid hash.
        for hash in self.gridhashes:
            # Deserialize the cell indexes from the grid hash and retrieve the cell size.
            xindex, yindex = map(int, hash.split(':'))
            left, top = xindex * CELL_SIZE[0], -yindex * CELL_SIZE[1]

            # Draw the grid cell.
            pygame.draw.polygon(background, (255, 255, 255), [
                                    (left, top),
                                    (left + CELL_SIZE[0], top),
                                    (left + CELL_SIZE[0], top + CELL_SIZE[1]),
                                    (left, top + CELL_SIZE[1])
                                ], 1)
        if self.__classname == "sprite":
            pass
                                

# Placeholder function.
def placeholder(sprite, *args):
    sprite._engine.console.log(f"Entity {sprite.get_class()}: engine/entity/entity.py placeholder function called!")

# Define what should be imported from this module.
__all__ = ["Entity", "MOVETYPE_NONE", "MOVETYPE_ANCHORED", 
           "MOVETYPE_PHYSICS", "MOVETYPE_CUSTOM"]