"""This is the top-level module of the entire engine code.

The base Engine class is defined here. It must be instantiated in your game code,
with the init() method called, in order to start the engine."""

import os
import pygame
import time
import argparse

from . import globals
from . import logger
from . import version
from . import gvar
from . import game_interface
from . import entity
from . import ui
from . import sound

# Engine-oriented timer, only invoked per frame.
class Timer():
    def __init__(self, func, end, *args):
        self.func = func
        self.end = end
        self.args = args

# The top-level engine class.
class LLEngine():
    # Construct an instance of the engine class.
    def __init__(self, name = "LLEngine"):
        # Set the name of this engine
        self.__name = name

        # Initialize Pygame and set up any crucial Pygame objects here.
        pygame.init()
        self.__clock = pygame.time.Clock()
        self.missing = None # Cached missing texture; must be set after the video mode is set!
        self.origin = pygame.Vector2(0, 0) # Used for the background.

        # Write the loaded mixer properties.
        mixer_init = pygame.mixer.get_init()
        sound.Sound.cached_sample_rate = mixer_init[0]
        sound.Sound.num_channels = mixer_init[2]

        # Initiate engine-specific data.
        self.globals = globals.GlobalVars()
        self.console = logger.Logger("Console")
        self.__gvars = dict()
        self.__game: game_interface.Game = None

        # Create new engine gvars.
        self.fps_max = self.create_gvar("fps_max", 60.0, 
                                        "Frame rate limiter. Set to 0 for unlimited FPS.")
        self.use_self_busywait = self.create_gvar("use_self_busywait", 0,
                                        "Use custom busy-wait code.")
        self.showfps = self.create_gvar("showfps", 0, "Display FPS counter.")
        
        # Create gvars for the renderer.
        self.width = self.create_gvar("width", 640, "Start-up width of the window.", min=0)
        self.height = self.create_gvar("height", 480, "Start-up height of the window.", min=0)
        self.game_width = self.create_gvar("game_width", 640, "Fixed game resolution width.",
                                           gvar.GVAR_PROGRAMONLY, 0)
        self.game_height = self.create_gvar("game_height", 480, "Fixed game resolution height.",
                                            gvar.GVAR_PROGRAMONLY, 0)
        
        # Create a list of timers. 
        self.__timers = []
        
        # Configure entities.
        self.__entity_head: entity.Entity = None
        self.__entity_tail: entity.Entity = None
        self.__entity_types = {
            "entity":   entity.Entity,
            "rect":     entity.Rectangle,
            "tile":     entity.Tile,
            "sprite":   entity.Sprite,
        }

        # Configure UI elements.
        self.__element_head: ui.Element = None
        self.__element_tail: ui.Element = None
        self.__background_head: ui.Element = None
        self.__background_tail: ui.Element = None
        self.__element_types = {
            "element":  ui.Element,
            "frame":    ui.Frame,
            "image":    ui.Image,
            "text":     ui.Text
        }
        self.__focused_text: ui.Text = None
        self.__focused_keydown = ("", pygame.K_0)
        self.__focused_timestamp = 0.0
        self.__focused_keyinterval = 0.0

        # Declare a text element for the graphical FPS counter.
        self.__fps_counter: ui.Text = None

        # Instantiate the physics engine.
        self.__physics = entity.LLPhysics(self)
        self.physics_enabled = True

        # Show that the engine has initialized.
        self.console.log(f"LLEngine v{version.major}.{version.minor}.{version.patch}")

    # Compose the allocated game instance with this engine.
    def set_game(self, game):
        self.__game = game

    # Start the main game loop.
    def init(self):
        # Fail if the game attribute has not been allocated.
        if not self.__game:
            self.console.error("Could not launch engine due to missing game field!")

        # Set the video mode temporarily, so that we can configure all image surfaces,
        # alongside the missing texture object.
        screen = pygame.display.set_mode((1, 1), pygame.RESIZABLE)
        missing_dir = os.path.join(os.path.dirname(__file__), "assets/missing.png")
        if not os.path.isfile(missing_dir):
            self.console.error(f"\"assets/missing.png\" not found!")
        self.missing = pygame.image.load(missing_dir).convert_alpha()

        # Record the instantiation of the engine and initialize the game.
        self.console.log("Instantiating engine")
        exception_thrown = False
        self.__game.init()

        # Fix the minimum values of the game's width and height.
        self.width.set_min(self.game_width.get())
        self.height.set_min(self.game_height.get())

        # Parse any command-line arguments using argparse, which can be used for
        # modifying any game variables.
        parser = argparse.ArgumentParser(prog=self.__name,
                                         description="A video game using LLEngine.")
        parser.add_argument("-m", "--modify", action="append", help="--modify gvar=value")
        args = parser.parse_args()

        # Read through any game variables that the user would like to manipulate.
        if args.modify:
            for arg in args.modify:
                # Locate the game variable.
                arg = arg.strip()
                split = arg.split("=", 1)
                if not split[0] in self.__gvars:
                    self.console.warn(f"game variable \"{split[0]}\" does not exist.")
                    continue

                # If we only have the variable name, print its details.
                name = split[0]
                var = self.__gvars[name]
                if len(split) < 2:
                    self.console.log(var)
                    continue

                # Check if the game variable can actually be modified.
                if var.flags & gvar.GVAR_PROGRAMONLY:
                    self.console.warn(f"game variable \"{name}\" cannot be modified.")
                    continue
                
                # Modify the game variable. Reject any invalid attempts (i.e. when the
                # type of the value provided is incorrect).
                value = split[1]
                try:
                    var.set(type(var.get())(value))
                    self.console.log(f"Set \"{name}\" to \"{var.get()}\".")
                except ValueError as ex:
                    self.console.warn(f"game variable \"{name}\" modification failed: \"{ex}\"")
        self.console.log("")

        # Create a new screen for the window, and a background surface, which everything will be
        # blit onto.
        screen = pygame.display.set_mode((self.width.get(), self.height.get()), pygame.RESIZABLE)
        pygame.display.set_caption(self.__name)
        background = pygame.Surface((self.game_width.get(), self.game_height.get()))

        # Main game loop: run the user-defined per-frame game code each frame.
        self.globals.fps = self.fps_max.get()
        engine_start = time.perf_counter()
        try:
            while True:
                # Timestamp for the beginning of this frame.
                start = time.perf_counter()
                
                # Read the events queue to check for any new Pygame events.
                quit = False
                for event in pygame.event.get():
                    # Quit Pygame upon exit.
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        quit = True
                        break

                    # If the user changes the window resolution, clamp it and re-adjust the
                    # width/height gvars.
                    elif event.type == pygame.VIDEORESIZE:
                        self.width.set(event.w)
                        self.height.set(event.h)
                        if self.width.get() != event.w or self.height.get() != event.h:
                            screen = pygame.display.set_mode((self.width.get(), self.height.get()),
                                                             pygame.RESIZABLE)
                            
                    # Check if we are pressing a new key.
                    elif event.type == pygame.KEYDOWN:
                        # Check if we are focused on a text element.
                        if self.focused():
                            # If this is the enter key, unfocus.
                            if event.key == pygame.K_RETURN:
                                self.unfocus_text(True)
                            else:
                                # Configure the new held down key.
                                self.__focused_timestamp = time.perf_counter()
                                self.__focused_keydown = (event.unicode, event.key)
                                self.__manipulate_text()

                        # Invoke the game's keydown method.
                        self.__game.keydown(event.key, event.unicode, self.focused())

                    # Check if we stopped pressing a key.
                    elif event.type == pygame.KEYUP:
                        # Check if we are focused on a text element.
                        if self.focused() and event.key == self.__focused_keydown[1]:
                            self.__focused_timestamp = -1.0

                        # Invoke the game's keydown method.
                        self.__game.keyup(event.key, event.unicode, self.focused())

                # If the Pygame quit signal was read, exit out of the loop.
                if quit:
                    break # Goto would be nice honestly.

                # Manipulate the focused text buffer repeatedly if we are pressing a key
                # and it has been >0.5s since we pressed said key.
                if (self.__focused_timestamp > 0 
                    and time.perf_counter() - self.__focused_timestamp > 0.5
                    and time.perf_counter() - self.__focused_keyinterval > 0.025):
                    self.__manipulate_text()
                    self.__focused_keyinterval = time.perf_counter()

                # Call the game and physics engines' per-frame methods.
                self.__game.per_frame()
                if self.physics_enabled:
                    self.__physics.per_frame()
                self.__game.post_physics()

                # Invoke and clear any expired timers.
                for timer in self.__timers:
                    if timer.end < start:
                        timer.func(*timer.args)
                self.__timers[:] = [timer for timer in self.__timers if timer.end >= start]

                # Clear the background surface prior to any drawing.
                background.fill((0, 0, 0))

                # Blit all background UI elements.
                element = self.__background_head
                while element:
                    if element.enabled:
                        element.invoke_event("draw", background)
                    element = element.next

                # Blit all entities.
                entity = self.__entity_head
                while entity:
                    # If the entity is active, call some important events.
                    if entity.active:
                        # Call the per-frame and draw events.
                        entity.invoke_event("per_frame")
                        if entity.draw:
                            entity.invoke_event("draw", background)

                        # For debugging, draw all the grid cells that the entity is in.
                        if entity.drawgrid:
                            entity.draw_grid(background)

                    # Go to the next entity.
                    entity = entity.next

                # Blit all foreground UI elements.
                element = self.__element_head
                while element:
                    if element.enabled:
                        element.invoke_event("draw", background)
                    element = element.next

                # Blit the FPS counter if it is configured.
                if self.showfps.get() and self.__fps_counter:
                    self.__fps_counter.invoke_event("draw", background)

                # Scale the background surface onto the current resolution of the window.
                scale = min(screen.get_width() / self.game_width.get(), 
                            screen.get_height() / self.game_height.get())
                frame = pygame.transform.scale_by(background, scale)
                
                # Manipulate the position of the frame surface.
                frame_rect = frame.get_rect(center = screen.get_rect().center)
                frame_rect = frame_rect.move(self.origin.x * scale, -self.origin.y * scale)

                # Blit the frame onto the screen and update the rendered output.
                screen.blit(frame, frame_rect)
                pygame.display.update()

                # Limit the framerate (if specified) and calculate the delta time and fps.
                end = 0
                if not self.use_self_busywait.get():
                    # Just call clock.tick() if using Pygame's Clock class.
                    self.__clock.tick(self.fps_max.get())
                    end = time.perf_counter()
                else:
                    # Busy-wait implementation (that unfortunately uses up the CPU)
                    # by infinitely looping until the delta time matches our framerate.
                    end = time.perf_counter()
                    if self.fps_max.get() > 0:
                        while (end - start) < (1 / self.fps_max.get()):
                            end = time.perf_counter()
                self.globals.frametime = end - start
                self.globals.fps = pygame.math.lerp(self.globals.fps,
                                                    1 / self.globals.frametime,
                                                    min(max(self.globals.frametime * 2, 0), 1))
                
                # Bump the frames counter and calculate the time length.
                self.globals.frames += 1
                self.globals.time = time.perf_counter() - engine_start

                # Display the FPS counter if showfps is toggled.
                if self.showfps.get():
                    # Create the FPS counter if it isn't already created.
                    if not self.__fps_counter:
                        self.__fps_counter = ui.Text(self, "text")
                        self.__fps_counter.load_default(12)
                        self.__fps_counter.set_size(ui.UDim2(0, 150, 0, 30))
                        self.__fps_counter.set_position(ui.UDim2(1, -160, 0, 10))
                        self.__fps_counter.set_x_align(ui.X_RIGHT)
                        self.__fps_counter.set_colour(pygame.Color(0, 128, 0))
                        self.__fps_counter.enabled = True
                    
                    # Display the current FPS.
                    self.__fps_counter.set_text(f"fps: {self.globals.fps:.0f}")

        # If an exception is caught, mark it and log it.
        except Exception as ex:
            exception_thrown = True
            self.console.log(f"*EXCEPTION* {ex}")
            raise
        
        # Call the atexit function when the engine exits.
        # Keyboard interrupts are caught here. This also works regardless of the
        # exception being re-thrown.
        finally:
            self.__game.atexit(exception_thrown)
            pygame.quit()

    # Create a new game variable.
    def create_gvar(self, name, value, description = "", flags = 0, min = None, max = None):
        # If it already exists, just return the existing one.
        if name in self.__gvars:
            return self.__gvars[name]
        
        # Create a new game variable.
        self.__gvars[name] = gvar.GameVar(name, value, description, flags, min, max)
        return self.__gvars[name] # Can't use walrus operator here?

    # Retrieve a game variable by name.
    def find_gvar(self, name):
        return self.__gvars[name]
    
    # Register a new entity type by classname.
    def register_classname(self, name, entity_type):
        self.__entity_types[name] = entity_type

    # Create a new entity by classname, assigning it to the entity linked list.
    def create_entity_by_class(self, classname, before = None):
        # Throw an error if the classname is invalid!
        if classname not in self.__entity_types:
            self.console.error(f"entity classname \"{classname}\" is invalid!")
        
        # Create a new entity by the classname.
        newEnt = self.__entity_types[classname](self, classname)

        # Link the entity to the entities linked list.
        if before:
            # Check that the given entity is an actual entity.
            if not isinstance(before, entity.Entity):
                self.console.error(f"object {id(before)} is not an entity!")

            # This entity should be linked before the given entity.
            newEnt.prev = before.prev
            if newEnt.prev:
                newEnt.prev.next = newEnt
            else:
                self.__entity_head = newEnt
            newEnt.next = before
            before.prev = newEnt
        else:
            # Insert the entity at the end of the linked list instead.
            newEnt.prev = self.__entity_tail
            if newEnt.prev:
                newEnt.prev.next = newEnt
            if not self.__entity_head:
                self.__entity_head = newEnt
            self.__entity_tail = newEnt

        # Return the entity.
        return newEnt
    
    # Activate an entity, thus rendering it and allowing interactions with it.
    def activate_entity(self, ent):
        ent.active = True
        ent.invoke_event("activated")
        self.__physics.insert_entity(ent)
    
    # Initiate the sequence of deleting an entity.
    def delete_entity(self, ent):
        # Ignore if this entity is already being deleted.
        if ent.deleted:
            return

        # Stop rendering this entity and create a timer for deleting it later.
        ent.draw = False
        ent.deleted = True
        ent.movetype = entity.MOVETYPE_NONE
        self.create_timer(self.__delete_entity, 0, ent)

    # Return the first entity instance in the engine.
    def entity_head(self):
        return self.__entity_head
    
    # Register a new element type by classname.
    def register_ui_classname(self, name, element_type):
        self.__element_types[name] = element_type

    # Create a new UI element by classname, assigning it to the element linked list.
    def create_ui_element_by_class(self, classname, layer = ui.LAYER_FOREGROUND):
        # Throw an error if the classname is invalid!
        if classname not in self.__element_types:
            self.console.error(f"ui element classname \"{classname}\" is invalid!")

        # Create a new element by the classname.
        newElem = self.__element_types[classname](self, classname)

        # Link the entity to the entities linked list.
        newElem.prev = (self.__element_tail if layer == ui.LAYER_FOREGROUND 
                       else self.__background_tail)
        if newElem.prev:
            newElem.prev.next = newElem
        if layer == ui.LAYER_FOREGROUND:
            if not self.__element_head:
                self.__element_head = newElem
            self.__element_tail = newElem
        else:
            if not self.__background_head:
                self.__background_head = newElem
            self.__background_tail = newElem

        # Return the entity.
        return newElem
    
    # Delete an element from the engine, thus unlinking it from the element linked list.
    def delete_ui_element(self, elem):
        if not elem.prev:
            if elem.layer == ui.LAYER_FOREGROUND:
                self.__element_head = elem.next
            else:
                self.__background_head = elem.next
        if not elem.next:
            if elem.layer == ui.LAYER_FOREGROUND:
                self.__element_tail = elem.prev
            else:
                self.__background_tail = elem.prev
        elem.unlink()
    
    # Return the first background element instance in the engine.
    def background_head(self):
        return self.__background_head
    
    # Return the first foreground element instance in the engine.
    def element_head(self):
        return self.__element_head
    
    # Focus a text element.
    def focus_text(self, text):
        if self.__focused_text and self.__focused_text != text:
            self.__focused_text.invoke_event("focuslost", False)
        self.__focused_text = text
        self.__focused_text.invoke_event("focused")
        self.__focused_keydown = ("", pygame.K_0)

    # Drop focus on a text element.
    def unfocus_text(self, enter_hit = False):
        self.__focused_text.invoke_event("focuslost", enter_hit)
        self.__focused_text = None
        self.__focused_timestamp = -1.0

    # Is the engine currently focused on a text element?
    # If so, retrieve the focused text element.
    def focused(self):
        return self.__focused_text
    
    # Manipulate the focused text buffer.
    def __manipulate_text(self):
        current = self.__focused_text.get_text()
        if self.__focused_keydown[1] == pygame.K_BACKSPACE:
            self.__focused_text.set_text(current[:-1])
        else:
            self.__focused_text.set_text(current + self.__focused_keydown[0])

    # Get all held keys.
    def get_keys_dict(self):
        return pygame.key.get_pressed()
    
    # Create a new sound instance.
    def create_sound(self, path = None):
        snd = sound.Sound(self)
        if path:
            snd.load(path)
        return snd
    
    # Create a new timer, which will be handled by the engine.
    def create_timer(self, func, length, *args):
        self.__timers.append(Timer(func, time.perf_counter() + length, *args))

    # Clear all background elements.
    def clear_background_elements(self):
        self.__background_head = None
        self.__background_tail = None

    # Clear all foreground elements.
    def clear_foreground_elements(self):
        self.__element_head = None
        self.__element_tail = None
    
    # Clear all entities.
    def clear_entities(self):
        # Nullify each entity's gridhashes array.
        ent = self.__entity_head
        while ent:
            ent.gridhashes = dict()
            ent = ent.next

        # Reset the physics engine and this engine's entity list.
        self.__physics.clear_entities()
        self.__entity_head = None
        self.__entity_tail = None

    # For a given set of start/end points forming a rectangle, return all the 
    # entities that are found within said rectangle.
    def query_entities(self, start, end, include_nocollide = True):
        # First, create the rectangle for testing collision.
        diff = end - start
        hitbox = pygame.Rect(start.x, -start.y, diff.x, -diff.y)

        # Get a list of entities within the appropriate grid cells from the
        # physics engine, and check whether they overlap with the given
        # rectangle, and return it.
        entities = self.__physics.query_entities(start, end, include_nocollide)
        entities[:] = [ent for ent in entities if hitbox.colliderect(ent._baserect)]
        return entities
    
    # Return all entities that are found within a given radius, i.e. return all entities
    # within a given circle.
    def query_entities_in_radius(self, centre, radius, include_nocollide = True):
        # Get a list of entities within the appropriate grid cells from the
        # physics engine, and check whether they are within the given radius.
        entities = self.__physics.query_entities(centre + pygame.math.Vector2(-radius, radius), 
                                                 centre + pygame.math.Vector2(radius, -radius), 
                                                 include_nocollide)
        entities[:] = [ent for ent in entities 
                       if ent.get_centre().distance_squared_to(centre) < radius ** 2]
        return entities
    
    # Get the number of entities that currently exist.
    def count_entities(self, active = True):
        ent = self.entity_head()
        count = 0
        while ent:
            if (active and ent.active) or not active:
                count += 1
            ent = ent.next
        return count
    
    # Delete an entity from the engine, thus unlinking it from the entity linked list.
    def __delete_entity(self, ent):
        # Remove the entity from the physics engine's grid.
        self.__physics.remove_entity(ent)

        # Unlink the entity from the entity linked list and delete it.
        if not ent.prev:
            self.__entity_head = ent.next
        if not ent.next:
            self.__entity_tail = ent.prev
        ent.unlink()