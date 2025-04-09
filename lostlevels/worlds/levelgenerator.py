"""The Lost Levels level generator is used to assist with level generation,
in order to create map tiles of varying lengths, alongside loading the
appropriate biome tilesheets/textures."""

import pygame
import engine
import lostlevels
import lostlevels.sprites

# Level data returned by a level.
class LevelData():
    # Create a new set of level data.
    def __init__(self, eng, level, player_offset, biome):
        # Bind the engine and game to this level data instance.
        self._engine = eng
        self._level = level

        # Store the biome name.
        self.biome = biome

        # Set the default player spawn position.
        self.player_offset = player_offset

        # Create a dictionary of groups of entities.
        self.groups = dict()

    # Called each frame.
    def per_frame(self):
        pass

    # Called each frame after the physics engine has computed
    # its calculations.
    def post_physics(self):
        pass

    # Called whne the game is being paused.
    def pause(self):
        pass

    # Called when the game is being unpaused.
    def unpause(self):
        pass

# The Lost Levels level generator class.
class LevelGenerator():
    # Create a new level generator.
    def __init__(self, eng, level, biome):
        # Bind the engine/game instances to this level generator.
        self.__engine = eng
        self.__level = level

        # Initialize the biome and therefore create the level's background.
        self.__biome = biome
        self.__level.backgroundmain = self.__engine.create_ui_element_by_class(
            "image", engine.ui.LAYER_BACKGROUND)
        self.__level.backgroundsecondary = self.__engine.create_ui_element_by_class(
            "image", engine.ui.LAYER_BACKGROUND)
        self.__level.backgroundmain.load(f"lostlevels/assets/biomes/{biome}/background.png")
        self.__level.backgroundsecondary.load(f"lostlevels/assets/biomes/{biome}/background.png")
        self.__level.backgroundmain.set_size(engine.ui.UDim2(2, 0, 1, 0))
        self.__level.backgroundsecondary.set_size(engine.ui.UDim2(2, 0, 1, 0))
        self.__level.backgroundmain.enabled = True
        self.__level.backgroundsecondary.enabled = True

    # Generate ground tiles.
    def generate_ground(self, offset, length = 1, height = 1, use_winter = True, draw = True, spiked = False):
        # If this is any other biome, just use the first entry tile.
        if self.__biome != "winter" and use_winter:
            return self.__generate_tiles("tile", 0, offset, length, height, draw, spiked)
        
        # The top layer must use the 20th entry tile. Underground tiles can use
        # the same entry as before.
        ents = self.__generate_tiles("tile", 19, offset, length, 1, draw, spiked)
        if height > 1:
            ents.extend(self.__generate_tiles(
                "tile", 0, offset + pygame.math.Vector2(0, -32), length, height - 1), draw, spiked)
        return ents
    
    # Generate destructible blocks.
    def generate_destructible(self, offset, length = 1, height = 1, draw = True, spiked = False):
        # Generate the tiles.
        ents = self.__generate_tiles("tile", 1, offset, length, height, draw, spiked)

        # Hook the collision and collisionfinal events of each of them.
        for ent in ents:
            ent.get_event("collision").set_func(
                lambda hit, other, coltype, coldir: self.__destroy_block_collide(hit, other, coltype, coldir))
            ent.get_event("collisionfinal").set_func(
                lambda hit, other, coltype, coldir: self.__destroy_block(hit, other, coltype, coldir))

        # Return the entities.
        return ents
    
    # Generate a small hill.
    def generate_hill(self, offset, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 3, offset, draw = draw, spiked = spiked)
        ents.extend(self.__generate_tiles("tile", 3, offset + pygame.math.Vector2(32, 0), 
                                          draw = draw, spiked = spiked))
        for ent in ents:
            ent.movetype = engine.entity.MOVETYPE_NONE
        ents[1].flip(flip_x = True)
        return ents
    
    # Generate a bush.
    def generate_bush(self, offset, length = 2, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 4, offset)
        if length > 2:
            ents.extend(self.__generate_tiles(
                "tile", 5, offset + pygame.math.Vector2(32, 0), length - 2, draw = draw, spiked = spiked))
        ents.extend(self.__generate_tiles(
            "tile", 4, offset + pygame.math.Vector2((length - 1) * 32, 0), draw = draw, spiked = spiked))
        for ent in ents:
            ent.movetype = engine.entity.MOVETYPE_NONE
        ents[-1].flip(flip_x = True)
        return ents
    
    # Generate a cloud.
    def generate_cloud(self, offset, length = 2, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 6, offset)
        if length > 2:
            ents.extend(self.__generate_tiles(
                "tile", 7, offset + pygame.math.Vector2(32, 0), length - 2, draw = draw, spiked = spiked))
        ents.extend(self.__generate_tiles(
            "tile", 6, offset + pygame.math.Vector2((length - 1) * 32, 0), draw = draw, spiked = spiked))
        for ent in ents:
            ent.movetype = engine.entity.MOVETYPE_NONE
        ents[-1].flip(flip_x = True)
        return ents
    
    # Generate a funny cloud. The movetype will not be set to handle collision events.
    def generate_funny_cloud(self, offset, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 6, offset)
        ents.extend(self.__generate_tiles("tile", 23, offset + pygame.math.Vector2(32, 0), 
                                          draw = draw, spiked = spiked))
        ents.extend(self.__generate_tiles("tile", 6, offset + pygame.math.Vector2(64, 0),
                                          draw = draw, spiked = spiked))
        ents[2].flip(flip_x = True)
        return ents
    
    # Generate blocks.
    def generate_blocks(self, offset, length = 1, height = 1, draw = True, spiked = False):
        return self.__generate_tiles("tile", 14, offset, length, height, draw, spiked)
    
    # Generate void tiles. Collision will be off by default.
    def generate_void(self, offset, length = 1, height = 1, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 15, offset, length, height, draw, spiked)
        for ent in ents:
            ent.movetype = engine.entity.MOVETYPE_NONE
        return ents

    # Generate an athletic platform.
    def generate_athletic(self, offset, length = 2, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 16, offset)
        if length > 2:
            ents.extend(self.__generate_tiles(
                "tile", 17, offset + pygame.math.Vector2(32, 0), length - 2, draw = draw, spiked = spiked))
        ents.extend(self.__generate_tiles(
            "tile", 16, offset + pygame.math.Vector2((length - 1) * 32, 0), draw = draw, spiked = spiked))
        ents[-1].flip(flip_x = True)
        return ents
    
    # Generate ropes that you can jump through.
    def generate_rope(self, offset, length = 1, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 18, offset, length, 1, draw, spiked)
        for ent in ents:
            ent.get_event("collision").set_func(
                lambda hit, other, coltype, coldir: self.__hit_rope(hit, other, coltype, coldir))
        return ents
    
    # Create a levitating platform. (This must be programmed manually!)
    def generate_platform(self, offset, length = 1, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 20, offset, length, 1, draw, spiked)
        for ent in ents:
            ent.movetype = engine.entity.MOVETYPE_CUSTOM
        return ents
    
    # Create a ballpoint.
    def generate_ballpoint(self, offset, draw = True, spiked = False):
        return self.__generate_tiles("tile", 21, offset, draw = draw, spiked = spiked)
    
    # Generate ice blocks.
    def generate_ice(self, offset, length = 1, height = 1, draw = True, spiked = False):
        ents = self.__generate_tiles("tile", 22, offset, length, height, draw, spiked)
        for ent in ents:
            ent.friction = 0.075
        return ents
    
    # Generate power-up blocks.
    def generate_powerup_block(self, offset, length = 1, height = 1, decoy = False, fall = False, 
                               draw = True, spiked = False):
        # First, generate the entities themselves.
        ents = self.__generate_sprites("powerup_block", offset, length, height, draw, spiked)
        
        # Modify the properties of each power-up block.
        for ent in ents:
            ent.biome = self.__biome
            ent.decoy = decoy
            ent.fall = fall
            ent.level = self.__level

        # Return the power-up blocks.
        return ents
    
    # Generate map coins.
    def generate_coin(self, offset, length = 1, height = 1, draw = True, spiked = False):
        ents = self.__generate_sprites("coin", offset, length, height, draw, spiked)
        for ent in ents:
            ent.level = self.__level
        return ents
    
    # Generate the main body of a pipe.
    def generate_pipe_body(self, offset, length = 1, orientation = lostlevels.sprites.PIPE_0):
        # Create tiles for the pipe body.
        ents = []
        for i in range(0, length):
            # Create the 1st entry tile.
            tile1 = self.__engine.create_entity_by_class("tile")
            tile1.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), 10 + orientation // 2)
            tile1.set_baseorigin(offset + self.__get_pipetile_offset(i * 2, orientation))
            tile1.rotate(-orientation * 90)
            ents.append(tile1)

            # Create the 2nd entry tile.
            tile2 = self.__engine.create_entity_by_class("tile")
            tile2.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), 11 - orientation // 2)
            tile2.set_baseorigin(offset + self.__get_pipetile_offset(i * 2 + 1, orientation))
            tile2.rotate(-orientation * 90)
            ents.append(tile2)
        
        # Return the tiles.
        return ents
    
    # Generate a 2x2 section of a pipe with roots for other pipes.
    def generate_pipe_2x2(self, offset, orientation = lostlevels.sprites.PIPE_0, 
                          leftroot = False, rightroot = False):
        # Create a pipe body of length 2.
        ents = []
        for i in range(0, 2):
            # Configure the tile indexes.
            if orientation // 2 > 0:
                tile1_index = 25 - i if leftroot else 11
                tile2_index = 13 - i if rightroot else 10
            else:
                tile1_index = 13 - i if leftroot else 10
                tile2_index = 25 - i if rightroot else 11

            # Create the 1st entry tile.
            tile1 = self.__engine.create_entity_by_class("tile")
            tile1.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), tile1_index)
            tile1.set_baseorigin(offset + self.__get_pipetile_offset(i * 2, orientation))
            tile1.rotate(-orientation * 90)
            ents.append(tile1)

            # Create the 2nd entry tile.
            tile2 = self.__engine.create_entity_by_class("tile")
            tile2.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), tile2_index)
            tile2.set_baseorigin(offset + self.__get_pipetile_offset(i * 2 + 1, orientation))
            tile2.rotate(-orientation * 90)
            ents.append(tile2)
        
        # Return the tiles.
        return ents
    
    # Generate the top of a pipe.
    def generate_pipe_top(self, offset, orientation = lostlevels.sprites.PIPE_0,
                          section = None, player_offset = None):
        # Create the 1st entry tile.
        tile1 = self.__engine.create_entity_by_class("pipetop")
        tile1.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), 8 + orientation // 2)
        tile1.set_baseorigin(offset + self.__get_pipetile_offset(0, orientation))
        tile1.rotate(-orientation * 90)
        tile1.level = self.__level
        tile1.section = section
        tile1.offset = player_offset
        tile1.rotation = orientation

        # Create the 2nd entry tile.
        tile2 = self.__engine.create_entity_by_class("pipetop")
        tile2.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), 9 - orientation // 2)
        tile2.set_baseorigin(offset + self.__get_pipetile_offset(1, orientation))
        tile2.rotate(-orientation * 90)
        tile2.level = self.__level
        tile2.section = section
        tile2.offset = player_offset
        tile2.rotation = orientation
        
        # Return the tiles.
        return [tile1, tile2]
    
    # Internal code for generating an array of tiles.
    def __generate_tiles(self, classname, index, offset, length = 1, height = 1, draw = True, spiked = False):
        ents = []
        for y in range(0, height):
            for x in range(0, length):
                ent = self.__engine.create_entity_by_class(classname)
                ent.load(f"lostlevels/assets/biomes/{self.__biome}/main.png", (32, 32), index)
                ent.set_baseorigin(offset + pygame.math.Vector2(x * 32, -y * 32))
                ent.draw = draw
                if spiked:
                    ent.get_event("collisionfinal").hook(
                        (lambda hit, name, returnValue, other, coltype, coldir: 
                            self.__create_spikes(hit, other)), True)
                ents.append(ent)
        return ents
    
    # Internal code for generating an array of sprites.
    def __generate_sprites(self, classname, offset, length = 1, height = 1, draw = True, spiked = False):
        ents = []
        for y in range(0, height):
            for x in range(0, length):
                ent = self.__engine.create_entity_by_class(classname)
                ent.set_baseorigin(offset + pygame.math.Vector2(x * 32, -y * 32))
                ent.draw = draw
                if spiked:
                    ent.get_event("collisionfinal").hook(
                        (lambda hit, name, returnValue, other, coltype, coldir: 
                            self.__create_spikes(hit, other)), True)
                ents.append(ent)
        return ents
    
    # If a destructible block is invisible, handle collision.
    def __destroy_block_collide(self, ent, other, coltype, coldir):
        # If this block is visible, return true in all cases.
        if ent.draw:
            return True
        
        # Otherwise, only return true if this is a player hitting from below.
        return (coldir == engine.entity.COLDIR_DOWN and other == self.__level.player
                and other.get_baseorigin().y < ent.get_baseorigin().y)
    
    # Destroy a destructible block.
    def __destroy_block(self, ent, other, coltype, coldir):
        # If the player has hit this block from below, destroy it!
        if other == self.__level.player and coldir == engine.entity.COLDIR_DOWN:
            # Delete the entity.
            self.__engine.delete_entity(ent)

            # Play a destruction sound.
            sfx = self.__engine.create_sound("lostlevels/assets/audio/objects/destructible_hit.ogg")
            sfx.volume = 1
            sfx.play()

            # Create a bunch of debris.
            for i in range(0, 4):
                block = self.__engine.create_entity_by_class("tile")
                block.movetype = engine.entity.MOVETYPE_PHYSICS
                block.get_event("collision").set_func(lambda *args: False)
                block.load(f"lostlevels/assets/biomes/{self.__biome}/broken.png", (16, 16), 0)
                block.set_baseorigin(ent.get_centre() + pygame.math.Vector2(-8, 8))
                block.velocity = pygame.math.Vector2(
                    75 if i < 2 else -75, 300 if 1 <= i < 3 else 200)
                self.__engine.activate_entity(block)
    
    # Handle collision with ropes.
    def __hit_rope(self, ent, other, coltype, coldir):
        # If an entity hit this rope from above, resolve the collision.
        if coldir == engine.entity.COLDIR_UP:
            # If the entity is already inside this element, ignore it.
            if other.get_bottomleft().y < ent.get_topleft().y:
                return False

            # Resolve the collision.
            return True

        # Otherwise, ignore the collision.
        return False
    
    # Internal code for getting the offset of a pipe tile.
    def __get_pipetile_offset(self, count, orientation):
        # Configure the conditions for calculating the offset of this tile.
        length_pos = count // 2
        offset = count % 2
        x_multiplier = bool(orientation & 1) * (-1 if orientation == lostlevels.sprites.PIPE_270 else 1)
        y_multiplier = (not bool(orientation & 1)) * (-1 if orientation == lostlevels.sprites.PIPE_180 else 1)
        
        # Calculate the offset and return it.
        x = 32 * length_pos * x_multiplier + 32 * offset * (x_multiplier == 0)
        y = 32 * length_pos * y_multiplier - 32 * offset * (y_multiplier == 0)
        return pygame.math.Vector2(x, y)
    
    # Create spikes that come out of a given entity and kill the player.
    def __create_spikes(self, ent, other):
        # Confirm whether this is the player entity.
        if other != self.__level.player:
            return engine.Event.DETOUR_CONTINUE
        
        # If the player is already dead, do not create any new spikes.
        if not self.__level.player.alive:
            return engine.Event.DETOUR_CONTINUE
        
        # Create spikes around this entity.
        spikes = self.__generate_tiles("tile", 2, pygame.math.Vector2(0, 0), 4)
        for i, spike in enumerate(spikes):
            x_multiplier = (not bool(i & 1))  * (-1 if i == 2 else 1)
            y_multiplier = bool(i & 1) * (-1 if i == 3 else 1)
            spike.movetype = engine.entity.MOVETYPE_NONE
            spike.rotate(90 - i * 90)
            spike.set_baseorigin(ent.get_baseorigin() 
                                 + pygame.math.Vector2(32 * y_multiplier, 32 * x_multiplier))
            
        # Kill the player.
        self.__level.death()

        # Continue.
        return engine.Event.DETOUR_CONTINUE