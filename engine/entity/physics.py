# To be quite frank, I have never written a game engine before, let alone
# a physics engine, and so I wouldn't say that this code is optimal.
# I've yet to study how physics engines operate, should I maintain 
# interest in such things.

# The problem as well is that this physics engine is mostly designed only
# with static props in mind. There's no actual proper physics between
# dynamic entities.

"""The physics engine, responsible for manipulating each entity
that has been defined to be under the influence of this engine."""

import pygame
import math 
from . import entity
from .. import gvar

# Named constants defining default engine properties.
DEFAULT_GRAVITY = 1350
DEFAULT_FRICTION = 800
DEFAULT_MINHEIGHT = -1000
CELL_SIZE = (75, 75)

# Flags for defining collision.
COLTYPE_COLLIDING = 0   # This entity is colliding another entity.
COLTYPE_COLLIDED = 1    # This entity is being collided by another entity.
COLDIR_LEFT = 0         # This entity is colliding/being collided from the left.
COLDIR_RIGHT = 1        # This entity is colliding/being collided from the right.
COLDIR_UP = 2           # This entity is colliding/being collided from upwards.
COLDIR_DOWN = 3         # This entity is colliding/being collided from downwards.

# Spatial hash grid implementation, which will be responsible for organizing
# entities.
class SpatialHashGrid():
    # A doubly-linked list for each cell, which will contain each grid node.
    # Grid nodes consist of the actual entity value, alongside the previous/next
    # node object references.
    class List():
        # Grid node class.
        class GridNode():
            def __init__(self, value):
                # Store the entity itself.
                self.value = value

                # Store the previous/next nodes for the doubly-linked list.
                self.prev = None
                self.next = None

        # Constructor for a new cells list.
        def __init__(self):
            self.head = None
            self.tail = None

    # Construct a new spatial hash grid.
    def __init__(self, cellsize):
        # Create a new hashmap (i.e. dictionary) to track all the cells. The
        # origin cell will be initialized by default.
        self.cells = {
            "0:0": SpatialHashGrid.List()
        }

        # Store the cell size as a separate vector.
        self.__cellsize = cellsize

    # Insert an entity into this grid.
    def insert(self, entity):
        # Retrieve the minimum and maximum cell indexes for this entity.
        min_indexes = self.__get_indexes(entity.get_baseorigin())   # Top-left corner
        max_indexes = self.__get_indexes(pygame.math.Vector2(       # Bottom-right corner
                                            entity.get_baseorigin().x + entity.get_hitbox().x,
                                            entity.get_baseorigin().y - entity.get_hitbox().y
                                        ))                          

        # Loop through the x/y co-ordinates to generate a list of hashes for all the cells
        # this entity is in, and thus adding the entity to each cell.
        entity.gridhashes = dict()
        y = min_indexes[1]
        while y >= max_indexes[1]:
            x = min_indexes[0]
            while x <= max_indexes[0]:
                # Create a new hash.
                hash = self.__get_hash((x, y))

                # Create a new cell for this hash if it doesn't exist.
                if hash not in self.cells:
                    self.cells[hash] = SpatialHashGrid.List()

                # Insert this entity to the respective cell.
                node = SpatialHashGrid.List.GridNode(entity)
                node.prev = self.cells[hash].tail
                if node.prev:
                    node.prev.next = node
                node.next = None
                if not self.cells[hash].head:
                    self.cells[hash].head = node
                self.cells[hash].tail = node

                # Update the entity's grid hashes dictionary.
                entity.gridhashes[hash] = node

                # Update the x co-ordinate.
                x += 1
            
            # Update the y co-ordinate.
            y -= 1

        # Unmark the entity as dirty.
        entity.dirty = False

    # Remove an entity from this grid, on the assumption that it is 
    # either being updated or it is being deleted.
    def remove(self, entity):
        # Loop through each grid node for this entity and update the linked list.
        for hash in entity.gridhashes:
            # Get the grid node for this hash.
            node = entity.gridhashes[hash]

            # Update the grid node's linked list.
            if node.prev:
                node.prev.next = node.next
            else:
                self.cells[hash].head = node.next
            if node.next:
                node.next.prev = node.prev
            else:
                self.cells[hash].tail = node.prev
            
            # Delete the node.
            del node

        # Nullify the entity's grid hashes dictionary.
        entity.gridhashes = None

    # For a given set of start/end points forming a rectangle, return all the 
    # entities within the grid cells that are found within said rectangle.
    def query_entities(self, start, end, include_nocollide = False):
        # Acquire the minimum/maximum cell indexes for the given start/end points.
        hashes = []
        min_indexes = self.__get_indexes(start)
        max_indexes = self.__get_indexes(end)

        # Loop through the indexes and generate hashes for all the cells included
        # or inbetween.
        y, y_hit = min_indexes[1], False
        while not y_hit:
            # Confirm whether the y-index is the max index.
            if y == max_indexes[1]:
                y_hit = True
            
            # Loop through each x-index.
            x, x_hit = min_indexes[0], False
            while not x_hit:
                # Confirm whether the x-index is the max index.
                if x == max_indexes[0]:
                    x_hit = True

                # Generate a hash and insert it.
                hash = self.__get_hash((x, y))
                hashes.append(hash)
                
                # Update the x co-ordinate.
                x = x + 1 if max_indexes[0] > min_indexes[0] else x - 1

            # Update the y co-ordinate.
            y = y + 1 if max_indexes[1] > min_indexes[1] else y - 1

        # Now, loop through each cell and profile a list of all the entities in each cell.
        entities = []
        for hash in hashes:
            if hash not in self.cells:
                continue
            node = self.cells[hash].head
            while node:
                if (node.value not in entities
                    and ((not include_nocollide and node.value.movetype != entity.MOVETYPE_NONE)
                         or include_nocollide)):
                    entities.append(node.value)
                node = node.next

        # Return all the queried entities.
        return entities

    # Update an entity.
    def update(self, entity):
        self.remove(entity)
        self.insert(entity)

    # Reset this grid, thus removing all entities from it.
    def reset(self):
        self.cells = {
            "0:0": SpatialHashGrid.List()
        }

    # Return the indexes of the cell a given point is located in.
    def __get_indexes(self, point):
        return (int(math.copysign(abs(point.x) // self.__cellsize.x, point.x)), 
                int(math.copysign(abs(point.y) // self.__cellsize.y, point.y)))

    # Construct a hash for a cell's indexes.
    def __get_hash(self, indexes):
        # Return a hash based on the cell indexes the point is based in.
        return f"{indexes[0]}:{indexes[1]}"

# The physics engine, responsible for handling each entity's physics.
class LLPhysics():
    # Construct an instance of the physics engine.
    def __init__(self, engine):
        # Compose this physics engine instance with the engine instance.
        self.__engine = engine

        # Set some physics-specific properties.
        self.__gravity = self.__engine.create_gvar("gravity", DEFAULT_GRAVITY, "The world gravity.",
                                                   gvar.GVAR_PROGRAMONLY)
        self.__friction = self.__engine.create_gvar("friction", DEFAULT_FRICTION,
                                                    "Default friction constant.", gvar.GVAR_PROGRAMONLY)
        self.__minheight = self.__engine.create_gvar("minheight", -1000,
                                                     "Entities that fall below this height will be killed.",
                                                     gvar.GVAR_PROGRAMONLY)
        
        # Create a new spatial hash grid for organizing all entities.
        self.__grid = SpatialHashGrid(pygame.math.Vector2(CELL_SIZE))

    # Insert an entity into the spatial hash grid.
    def insert_entity(self, entity):
        return self.__grid.insert(entity)
    
    # Remove an entity from the spatial hash grid.
    def remove_entity(self, entity):
        self.__grid.remove(entity)

    # Per-frame method which runs physics code on each entity.
    def per_frame(self):
        # Walk through each entity in the engine's entity list.
        ent = self.__engine.entity_head()
        while (ent):
            # Skip if this entity is deactivated.
            if not ent.active:
                ent = ent.next
                continue

            # Skip if this entity is not defined to be manipulated, but make sure it is
            # actually updated in the spatial hash grid if it is marked dirty.
            if ent.movetype < entity.MOVETYPE_PHYSICS:
                if ent.dirty:
                    self.__grid.update(ent)
                ent = ent.next
                continue

            # Only manipulate the velocity vector if the movetype of this entity is
            # MOVETYPE_PHYSICS.
            if ent.movetype == entity.MOVETYPE_PHYSICS:
                # Inflict gravity upon this entity.
                ent.velocity.y -= self.__gravity.get() * self.__engine.globals.frametime

                # Handle friction. This is done through multiplication in order to handle
                #  +/- numbers, mathematically.
                if ent.groundentity:
                    newspeed = max(0, abs(ent.velocity.x) - self.__friction.get() 
                                   * ent.groundentity.friction * ent.friction 
                                   * self.__engine.globals.frametime)
                    if abs(ent.velocity.x) > 0:
                        newspeed /= abs(ent.velocity.x)
                    ent.velocity.x *= newspeed

                # Accelerate the entity based on its move value.
                # Inspired by:
                # https://github.com/id-Software/Quake-III-Arena/blob/master/code/game/bg_pmove.c
                difference = ent.move - ent.velocity.x
                if math.copysign(ent.move, difference) != ent.move:
                    difference = 0
                acceleration = (ent.acceleration * self.__engine.globals.frametime * ent.move
                                * ent.friction)
                if ent.groundentity:
                    acceleration *= ent.groundentity.friction
                if abs(acceleration) > abs(difference):
                    # Cap the acceleration speed if it means that the entity will move faster than
                    # its maximum speed.
                    acceleration = difference
                ent.velocity.x += acceleration

            # Before beginning collision detection, calculate the start and end points
            # in order to acquire all the grid cells.
            if ent.velocity.x >= 0 and ent.velocity.y >= 0:
                start = ent.get_bottomleft()
                end = ent.get_topright() + ent.velocity * self.__engine.globals.frametime
            elif ent.velocity.x >= 0 and ent.velocity.y < 0:
                start = ent.get_topleft()
                end = ent.get_bottomright() + ent.velocity * self.__engine.globals.frametime
            elif ent.velocity.x < 0 and ent.velocity.y >= 0:
                start = ent.get_bottomright()
                end = ent.get_topleft() + ent.velocity * self.__engine.globals.frametime
            else:
                start = ent.get_topright()
                end = ent.get_bottomleft() + ent.velocity * self.__engine.globals.frametime
            
            # Calculate all the entities that the entity may have hit and walk through
            # them.
            entities = self.__grid.query_entities(start, end)
            closest_x, x_diff = None, 0
            closest_y, y_diff = None, 0
            for collideent in entities:
                # Check if the collision entity is the same as the current entity.
                if collideent == ent:
                    continue

                # Check if collision was made by moving right.
                if (ent.velocity.x > 0 and end.x > collideent.get_topleft().x 
                    and start.x < collideent.get_topleft().x):
                    # Make sure that the two entities actually horizontally collide by performing
                    # AABB collision checks.
                    if ent.collides_y(collideent):
                        # Call the collision event on both entities and only continue colliding
                        # if both calls return True.
                        if (not ent.invoke_event("collision", collideent, COLTYPE_COLLIDING, COLDIR_LEFT)
                            or not collideent.invoke_event("collision", ent, COLTYPE_COLLIDED, COLDIR_LEFT)):
                            continue

                        # Calculate the difference in position between the right of the entity
                        # and the left of the collision entity.
                        diff = abs(abs(collideent.get_topleft().x) - abs(ent.get_topright().x))

                        # If the difference between the two entities are less than the previous
                        # cached difference, or the final collided entity is not set, set the 
                        # final collided entity to this collided entity.
                        if not closest_x or diff < x_diff:
                            closest_x = collideent
                            x_diff = diff

                        # If the other entity is a physics entity and this is a custom physics
                        # entity, move it.
                        if (ent.movetype == entity.MOVETYPE_CUSTOM 
                            and collideent.movetype == entity.MOVETYPE_PHYSICS):
                            collideent.set_baseorigin(collideent.get_baseorigin()
                                + pygame.math.Vector2(ent.velocity.x * self.__engine.globals.frametime, 0))
                
                # Check if collision was made by moving left.
                elif (ent.velocity.x < 0 and end.x < collideent.get_topright().x
                      and start.x > collideent.get_topright().x):
                    # Make sure that the two entities actually horizontally collide by performing
                    # AABB collision checks.
                    if ent.collides_y(collideent):
                        # Call the collision event on both entities and only continue colliding
                        # if both calls return True.
                        if (not ent.invoke_event("collision", collideent, COLTYPE_COLLIDING, COLDIR_RIGHT)
                            or not collideent.invoke_event("collision", ent, COLTYPE_COLLIDED, COLDIR_RIGHT)):
                            continue

                        # Calculate the difference in position between the left of the entity
                        # and the right of the collision entity.
                        diff = abs(abs(collideent.get_topright().x) - abs(ent.get_topleft().x))

                        # If the difference between the two entities are less than the previous
                        # cached difference, or the final collided entity is not set, set the 
                        # final collided entity to this collided entity.
                        if not closest_x or diff < x_diff:
                            closest_x = collideent
                            x_diff = diff

                        # If the other entity is a physics entity and this is a custom physics
                        # entity, move it.
                        if (ent.movetype == entity.MOVETYPE_CUSTOM 
                            and collideent.movetype == entity.MOVETYPE_PHYSICS):
                            collideent.set_baseorigin(collideent.get_baseorigin()
                                + pygame.math.Vector2(ent.velocity.x * self.__engine.globals.frametime, 0))

                # Check if collision was made by moving upwards.
                if (ent.velocity.y > 0 and end.y > collideent.get_bottomleft().y
                    and start.y < collideent.get_bottomleft().y):
                    # Make sure that the two entities actually horizontally collide by performing
                    # AABB collision checks.
                    if ent.collides_x(collideent):
                        # Call the collision event on both entities and only continue colliding
                        # if both calls return True.
                        if (not ent.invoke_event("collision", collideent, COLTYPE_COLLIDING, COLDIR_DOWN)
                            or not collideent.invoke_event("collision", ent, COLTYPE_COLLIDED, COLDIR_DOWN)):
                            continue

                        # Calculate the difference in position between the top of the entity
                        # and the bottom of the collision entity.
                        diff = abs(abs(collideent.get_bottomleft().y) - abs(ent.get_topleft().y))

                        # If the difference between the two entities are less than the previous
                        # cached difference, or the final collided entity is not set, set the 
                        # final collided entity to this collided entity.
                        if not closest_y or diff < y_diff:
                            closest_y = collideent
                            y_diff = diff

                        # If the other entity is a physics entity and this is a custom physics
                        # entity, move it.
                        if (ent.movetype == entity.MOVETYPE_CUSTOM 
                            and collideent.movetype == entity.MOVETYPE_PHYSICS):
                            collideent.set_baseorigin(collideent.get_baseorigin()
                                 + pygame.math.Vector2(0, ent.velocity.y * self.__engine.globals.frametime))
                            collideent.groundentity = ent

                # Check if collision was made by moving downwards.
                elif (ent.velocity.y < 0 and end.y < collideent.get_topleft().y
                      and start.y > collideent.get_topleft().y):
                    # Make sure that the two entities actually horizontally collide by performing
                    # AABB collision checks.
                    if ent.collides_x(collideent):
                        # Call the collision event on both entities and only continue colliding
                        # if both calls return True.
                        if (not ent.invoke_event("collision", collideent, COLTYPE_COLLIDING, COLDIR_UP)
                            or not collideent.invoke_event("collision", ent, COLTYPE_COLLIDED, COLDIR_UP)):
                            continue

                        # Calculate the difference in position between the bottom of the entity
                        # and the top of the collision entity.
                        diff = abs(abs(collideent.get_topleft().y) - abs(ent.get_bottomleft().y))

                        # If the difference between the two entities are less than the previous
                        # cached difference, or the final collided entity is not set, set the 
                        # final collided entity to this collided entity.
                        if not closest_y or diff < y_diff:
                            closest_y = collideent
                            y_diff = diff

                        # If the other entity is a physics entity and this is a custom physics
                        # entity, move it.
                        if (ent.movetype == entity.MOVETYPE_CUSTOM 
                            and collideent.movetype == entity.MOVETYPE_PHYSICS):
                            collideent.set_baseorigin(collideent.get_baseorigin()
                                + pygame.math.Vector2(0, ent.velocity.y * self.__engine.globals.frametime))
                                
            # Basic collision resolution if this entity's being manipulated by the physics engine.
            origin = ent.get_baseorigin()
            ent.groundentity = None
            if ent.movetype == entity.MOVETYPE_PHYSICS:
                # Handle horizontal collision.
                if closest_x:
                    # Call the collisionfinal event on both entities.
                    coldir = COLDIR_LEFT if ent.velocity.x > 0 else COLDIR_RIGHT
                    ent.invoke_event("collisionfinal", closest_x, COLTYPE_COLLIDING, coldir)
                    closest_x.invoke_event("collisionfinal", ent, COLTYPE_COLLIDED, coldir)

                    # Resolve this entity's velocity and origin.
                    if coldir == COLDIR_LEFT:
                        origin.x = closest_x.get_topleft().x - ent.get_hitbox().x
                    else:
                        origin.x = closest_x.get_topright().x
                    ent.velocity.x = 0

                # Handle vertical collision.
                if closest_y:
                    # Call the collisionfinal event on both entities.
                    coldir = COLDIR_DOWN if ent.velocity.y > 0 else COLDIR_UP
                    ent.invoke_event("collisionfinal", closest_y, COLTYPE_COLLIDING, coldir)
                    closest_y.invoke_event("collisionfinal", ent, COLTYPE_COLLIDED, coldir)

                    # Resolve this entity's velocity and origin.
                    if coldir == COLDIR_DOWN:
                        origin.y = closest_y.get_bottomleft().y
                    else:
                        origin.y = closest_y.get_topleft().y + ent.get_hitbox().y
                        ent.groundentity = closest_y
                    ent.velocity.y = 0

            # Set the new origin of this entity and update it in the grid.
            ent.set_baseorigin(origin + ent.velocity * self.__engine.globals.frametime)
            if ent.dirty:
                self.__grid.update(ent)

            # Kill this entity if it falls below minheight:
            if ent.get_baseorigin().y < self.__minheight.get():
                oldent, ent = ent, ent.next
                self.__engine.delete_entity(oldent)
                continue

            # Get the next entity.
            ent = ent.next

    # Remove all entities from the spatial hash grid.
    def clear_entities(self):
        self.__grid.reset()

    # For a given set of start/end points forming a rectangle, return all the 
    # entities within the grid cells that are found within said rectangle.
    def query_entities(self, start, end, include_nocollide = True):
        return self.__grid.query_entities(start, end, include_nocollide)
    
# Define what should be imported from this module.
__all__ = ["LLPhysics", "COLTYPE_COLLIDING", "COLTYPE_COLLIDED", 
           "COLDIR_LEFT", "COLDIR_RIGHT", "COLDIR_UP", "COLDIR_DOWN"]