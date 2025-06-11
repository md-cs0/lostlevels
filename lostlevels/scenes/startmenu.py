"""The start menu scene for Lost Levels."""

import os
import sys
import time
import pygame
import engine

from .. import savefile

# Save text element.
class SaveText(engine.ui.Text):
    # Construct the save text element.
    def __init__(self, engine, classname):
        # Call the element constructor and modify its default properties.
        super().__init__(engine, classname)
        self.save = None

# Start menu scene.
class StartMenu(engine.Game):
    # Construct the start menu.
    def __init__(self, eng, game):
        # Initialize the game interface.
        super().__init__(eng)
        self.__game = game
        self._engine.console.log("[Lost Levels]: launching start menu")
        
        # Register SaveText as an engine element type.
        self._engine.register_ui_classname("savetext", SaveText)

        # Create the background.
        self.sky = self._engine.create_ui_element_by_class("image", engine.ui.LAYER_BACKGROUND)
        self.sky.load("lostlevels/assets/biomes/overground/background.png")
        self.sky.set_size(engine.ui.UDim2(1, 0, 1, 0), False)
        self.sky.enabled = True

        # Load the introduction text.
        self.text = self._engine.create_ui_element_by_class("image")
        self.text.load("lostlevels/assets/start/lost levels.png")
        self.text.set_size(engine.ui.UDim2(1, 0, 1, 0))
        self.text.enabled = True

        # Create the new save button.
        self.newsave = self._engine.create_ui_element_by_class("text")
        self.newsave.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.newsave.set_size(engine.ui.UDim2(0, 200, 0, 20))
        self.newsave.set_position(engine.ui.UDim2(0.5, -100, 0.5, 0))
        self.newsave.set_text("NEW SAVE")
        self.newsave.set_colour(pygame.Color(255, 255, 255))
        self.newsave.set_x_align(engine.ui.X_CENTRE)
        self.newsave.enabled = True
        self.newsave.get_event("selected").set_func(lambda elem: self.input_newsave())

        # Create the load save button.
        self.loadsave = self._engine.create_ui_element_by_class("text")
        self.loadsave.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.loadsave.set_size(engine.ui.UDim2(0, 200, 0, 20))
        self.loadsave.set_position(engine.ui.UDim2(0.5, -100, 0.5, 20))
        self.loadsave.set_text("LOAD SAVE")
        self.loadsave.set_colour(pygame.Color(255, 255, 255))
        self.loadsave.set_x_align(engine.ui.X_CENTRE)
        self.loadsave.enabled = True
        self.loadsave.get_event("selected").set_func(lambda elem: self.input_loadsave())

        # Create the help button.
        self.help = self._engine.create_ui_element_by_class("text")
        self.help.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.help.set_size(engine.ui.UDim2(0, 200, 0, 20))
        self.help.set_position(engine.ui.UDim2(0.5, -100, 0.5, 40))
        self.help.set_text("HELP!")
        self.help.set_colour(pygame.Color(255, 255, 255))
        self.help.set_x_align(engine.ui.X_CENTRE)
        self.help.enabled = True
        self.help.get_event("selected").set_func(lambda elem: self.input_help())

        # Create the quit button.
        self.quit = self._engine.create_ui_element_by_class("text")
        self.quit.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.quit.set_size(engine.ui.UDim2(0, 200, 0, 20))
        self.quit.set_position(engine.ui.UDim2(0.5, -100, 0.5, 60))
        self.quit.set_text("QUIT")
        self.quit.set_colour(pygame.Color(255, 255, 255))
        self.quit.set_x_align(engine.ui.X_CENTRE)
        self.quit.enabled = True
        self.quit.get_event("selected").set_func(lambda elem: self.input_exit())

        # Append all the buttons to a list.
        self.buttons = [self.newsave, self.loadsave, self.help,
                        self.quit]
        
        # Draw a selector.
        self.selected_index = 0
        self.selector = self._engine.create_ui_element_by_class("frame")
        self.selector.set_size(engine.ui.UDim2(0, 10, 0, 10))
        self.selector.enabled = True

        # Create a text dialogue that appears after 10s if the user
        # does not select a button.
        self.help_dialogue = self._engine.create_ui_element_by_class("text")
        self.help_dialogue.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.help_dialogue.set_size(engine.ui.UDim2(0, 200, 0, 100))
        self.help_dialogue.set_position(engine.ui.UDim2(1, -220, 0.5, -14))
        self.help_dialogue.set_text("USE THE ARROW\nKEYS AND HIT\nENTER TO" \
                                    " SELECT\nA BUTTON!")
        self.help_dialogue.set_colour(pygame.Color(255, 255, 255))
        self.help_dialogue.set_y_align(engine.ui.Y_CENTRE)

        # Create a timestamp since the start menu launched and whether we
        # already selected a button.
        self.launch = time.perf_counter()
        self.selected = False

        # Create a text element for the help page, which is disabled by
        # default.
        self.help_page = self._engine.create_ui_element_by_class("text")
        self.help_page.load_localfont("lostlevels/assets/fonts/nes.ttf", 11)
        self.help_page.set_size(engine.ui.UDim2(1, -75, 0, 300))
        self.help_page.set_position(engine.ui.UDim2(0, 37, 0.5, 0))
        self.help_page.set_text("- USE UP AND DOWN KEYS TO NAVIGATE ON A MENU\n\n"  \
                                "- HIT ENTER TO TOGGLE A BUTTON OR EXIT A MENU\n\n" \
                                "- USE LEFT AND RIGHT KEYS TO MOVE PLAYER\n\n"      \
                                "- USE DOWN KEY TO CROUCH\n\n"                      \
                                "- HOLD Z TO SPRINT AND USE POWER-UP\n\n"           \
                                "- PRESS X TO JUMP\n\n"                             \
                                "- PRESS E TO USE ENTITY\n\n"                       \
                                "- PRESS P TO PAUSE\n\n"                            \
                                "- PRESS ESC TO EXIT GAME\n\n\n\n"                  \
                                "HIT ENTER TO RETURN TO MENU")
        self.help_page.set_colour(pygame.Color(255, 255, 255))
        self.help_page.set_x_align(engine.ui.X_CENTRE)

        # Create a helper dialogue for inputting the new save, disabled by default.
        self.newsave_help = self._engine.create_ui_element_by_class("text")
        self.newsave_help.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.newsave_help.set_size(engine.ui.UDim2(0, 400, 0, 32))
        self.newsave_help.set_position(engine.ui.UDim2(0.5, -200, 0.5, 0))
        self.newsave_help.set_text("INPUT YOUR NEW SAVE NAME BELOW:")
        self.newsave_help.set_colour(pygame.Color(255, 255, 255))
        self.newsave_help.set_x_align(engine.ui.X_CENTRE)

        # Create a text box for inputting the new save, disabled by default.
        self.newsave_box = self._engine.create_ui_element_by_class("text")
        self.newsave_box.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.newsave_box.set_size(engine.ui.UDim2(1, -100, 0, 20))
        self.newsave_box.set_position(engine.ui.UDim2(0, 50, 0.5, 32))
        self.newsave_box.set_text("")
        self.newsave_box.set_colour(pygame.Color(255, 255, 255))
        self.newsave_box.set_x_align(engine.ui.X_LEFT)
        self.newsave_box.get_event("focuslost").set_func(lambda elem, enter_hit: 
                                                         self.newsave_written(enter_hit))

        # Create a small bar below the text box for cosmetic purposes, disabled by default.
        self.newsave_box_bar = self._engine.create_ui_element_by_class("frame")
        self.newsave_box_bar.set_size(engine.ui.UDim2(1, -100, 0, 2))
        self.newsave_box_bar.set_position(engine.ui.UDim2(0, 50, 0.5, 52))
        self.newsave_box_bar.set_colour(pygame.Color(255, 255, 255))

        # Create a helper dialogue for the load save page.
        self.loadsave_help =  self._engine.create_ui_element_by_class("text")
        self.loadsave_help.load_localfont("lostlevels/assets/fonts/nes.ttf")
        self.loadsave_help.set_size(engine.ui.UDim2(0, 400, 0, 72))
        self.loadsave_help.set_position(engine.ui.UDim2(0.5, -200, 0.5, 0))
        self.loadsave_help.set_text("SCROLL UP AND DOWN AND HIT ENTER\nTO LOAD A SAVE.\n\n" \
                                   "HIT ESC TO GO BACK TO THE\nMAIN MENU.")
        self.loadsave_help.set_colour(pygame.Color(255, 255, 255))
        self.loadsave_help.set_x_align(engine.ui.X_CENTRE)

        # Create the saves directory if it doesn't currently exist.
        if not os.path.isdir("saves"):
            os.mkdir("saves")

    # Per-frame code.
    def per_frame(self):
        # If we are in the load save page, scroll buttons based on the selector's
        # position.
        if self.loadsave_help.enabled:
            for i, button in enumerate(self.buttons):
                # Position the button based on where we are in the list.
                topindex = (self.selected_index // 4) * 4
                button.set_position(engine.ui.UDim2(
                    0.5, -175, 0.5, 72 + (i - topindex) * 20))
                
                # Toggle the button's visiblity if it is in the top 4.
                button.enabled = topindex <= i < topindex + 4
        
        # Move the selector so that it is aligned with the button
        # currently selected.
        if self.loadsave_help.enabled:
            self.selector.set_position(self.buttons[self.selected_index].get_position()
                                    - engine.ui.UDim2(0, 20, 0, 0))
        else:
            self.selector.set_position(self.buttons[self.selected_index].get_position()
                                    + engine.ui.UDim2(0, 20, 0, 0))
        
        # Show the help dialogue if it has been 10s since launching and if we
        # have not previously selected a button.
        if time.perf_counter() - self.launch > 10 and not self.selected:
            self.help_dialogue.enabled = True
        
    # Handle input on keyup.
    def keyup(self, enum, unicode, focused):
        # Move the selector up if the key pressed is the up arrow key.
        if enum == pygame.K_UP:
            self.selected_index = (self.selected_index - 1) % len(self.buttons)
        
        # Move the selector down if the key pressed is the down arrow key.
        elif enum == pygame.K_DOWN:
            self.selected_index = (self.selected_index + 1) % len(self.buttons)

        # Select this button if we hit enter.
        elif enum == pygame.K_RETURN:
            # Check if we are in the help page.
            if self.help_page.enabled:
                self.input_help()

            # If we are in the new save page, just ignore.
            elif self.newsave_box.enabled:
                pass
            
            # This is a button, select it instead.
            else:
                self._engine.console.log(
                    f"[Lost Levels]: \"{self.buttons[self.selected_index].get_text()}\" selected")
                self.buttons[self.selected_index].invoke_event("selected")
                self.selected = True
                self.selected_index = 0

        # Return back to the main menu if ESC was pressed and we are in the 
        # load save page.
        elif enum == pygame.K_ESCAPE: # Modified condition so that it only checks for ESC input.
            # Check if we are in the help page.
            if self.help_page.enabled:
                self.input_help()

            # Are we in the load save page?
            elif self.loadsave_help.enabled == True:
                # Delete all the save buttons and disable the load save helper 
                # dialogue.
                self.loadsave_help.enabled = False
                for button in self.buttons:
                    self._engine.delete_ui_element(button)
            
            # If not, are we in the new save page?
            elif self.newsave_help.enabled == True:
                # Stop focusing on the new save text box and disable the new save
                # elements. Furthermore, re-enable the selector and clear the current input.
                self._engine.unfocus_text()
                self.newsave_box.set_text("")
                self.newsave_box.enabled = False
                self.newsave_help.enabled = False
                self.newsave_box_bar.enabled = False
                self.selector.enabled = True
            
            # Otherwise, forfeit.
            else:
                return
            
            # Re-toggle the main menu buttons.
            self.buttons = [self.newsave, self.loadsave, self.help,
                        self.quit]
            for button in self.buttons:
                button.enabled = True
            self.selected_index = 0

    # Create a new save.
    def input_newsave(self):
        # Disable the selector, buttons and help dialogue.
        self.help_dialogue.enabled = False
        self.selector.enabled = False
        for button in self.buttons:
            button.enabled = False

        # Enable the new save textbox and select it.
        self.newsave_box.enabled = True
        self._engine.focus_text(self.newsave_box)

        # Enable the new save help dialogue and the textbox bar.
        self.newsave_help.enabled = True
        self.newsave_box_bar.enabled = True

    # Load an existing save, or default to creating a new save if
    # there are no save files.
    def input_loadsave(self):
        # Query all the save files in the saves directory.
        files = [save for save in os.listdir("saves") if os.path.isfile(os.path.join("saves", save))]
        saves = []
        for file in files:
            save = savefile.LLSV(os.path.splitext(file)[0])
            if (error := save.read("saves")):
                self._engine.console.warn(f"[Lost Levels]: couldn't load save \"{file}\": {error}")
            else:
                saves.append(save)

        # If we don't have any save files, go to the new save prompt 
        # and return.
        if len(saves) == 0:
            self.input_newsave()
            return
        
        # Disable all the main menu buttons and help dialogue, and clear the buttons
        # array.
        self.help_dialogue.enabled = False
        for button in self.buttons:
            button.enabled = False
        self.buttons = []
        
        # Fill the buttons array with dynamically-created buttons for each save.
        for i, save in enumerate(saves):
            button = self._engine.create_ui_element_by_class("savetext")
            button.load_localfont("lostlevels/assets/fonts/nes.ttf")
            button.set_size(engine.ui.UDim2(0, 350, 0, 20))
            button.set_text(f"{i + 1} - {save.name.upper()}")
            button.set_colour(pygame.Color(255, 255, 255))
            button.set_x_align(engine.ui.X_CENTRE)
            button.enabled = True
            button.save = save
            button.get_event("selected").set_func(lambda elem: self.save_loaded(elem))
            self.buttons.append(button)

        # Enable the load save helper dialogue.
        self.loadsave_help.enabled = True
                
    # Toggle the help section.
    def input_help(self):
        # Toggle the selector, buttons and help page.
        self.help_page.enabled = not self.help_page.enabled
        self.selector.enabled = not self.selector.enabled
        for button in self.buttons:
            button.enabled = not button.enabled

        # Always disable the help dialogue.
        self.help_dialogue.enabled = False

    # Handle exit.
    def input_exit(self):
        self._engine.console.log("[Lost Levels]: exiting!")
        sys.exit(0)

    # Handle writing a new save.
    def newsave_written(self, enter_hit):
        # Do not create a save if the ENTER key was not hit.
        if not enter_hit:
            return

        # Check if the save file already exists.
        path = os.path.join("saves", self.newsave_box.get_text() + ".sav")
        if os.path.exists(path):
            # Alert the user that the save already exists and re-select the
            # text box.
            self.newsave_help.set_text("THIS SAVE ALREADY EXISTS!\nINPUT YOUR SAVE NAME BELOW:")
            self._engine.create_timer(self._engine.focus_text, 0, self.newsave_box)
            return
        
        # Create a nested function for handling invalid save names.
        def invalid_name(self):
            self.newsave_help.set_text("THE GIVEN SAVE NAME IS INVALID!\nINPUT YOUR SAVE NAME BELOW:")
            self._engine.create_timer(self._engine.focus_text, 0, self.newsave_box)

        # If the save name is empty, do not create a save.
        if self.newsave_box.get_text() == "":
            invalid_name(self)
            return

        # Create the save and load the game.
        try:
            self.__game.save = savefile.LLSV(self.newsave_box.get_text())
            self.__game.save.write("saves")
            self._engine.console.log(f"[Lost Levels]: created new save \"{self.newsave_box.get_text()}.sav\"")
            self.__game.load_levelselection()
        except OSError:
            invalid_name(self)

    # Handle loading an existing save.
    def save_loaded(self, elem):
        # Load the save and therefore load the game.
        self.__game.save = elem.save
        self._engine.console.log(f"[Lost Levels]: loaded save \"{elem.save.name}.sav\"")
        self.__game.load_levelselection()