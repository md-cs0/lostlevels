"""A text element that displays text, which can also be updated
if chosen."""

import pygame

from ..event import Event
from . import element

# Text alignment options.
X_LEFT      = 0
X_CENTRE    = 1
X_RIGHT     = 2
Y_TOP       = 0
Y_CENTRE    = 1
Y_BOTTOM    = 2

# Text element.
class Text(element.Element):
    # Construct a new text.
    def __init__(self, engine, classname):
        # Call the element constructor and modify its default properties.
        super().__init__(engine, classname)
        self.get_event("draw").set_func(Text.draw_text)

        # Text properties.
        self.__text = ""
        self.__texture = None
        self.__font = None
        self.__x_align = X_LEFT
        self.__y_align = Y_TOP
        self.__colour = pygame.Color(0, 0, 0)
        self.__antialiasing = True
        self.__bold = False
        self.__italic = False
        self.__underline = False

        # Focus events.
        self.set_event(Event("focused", lambda self: None))
        self.set_event(Event("focuslost", lambda self, enter_hit: None))

    # Load a font from a local font file. If the font path is invalid,
    # Pygame will default to the default font.
    def load_localfont(self, path, size = 12):
        try:
            self.__font = pygame.font.Font(path, size)
        except FileNotFoundError:
            self._engine.console.warn(f"font path \"{path}\" is invalid!")
            self.load_default()
    
    # Load a font from a system font. If the font provided does not exist, 
    # Pygame will default to the default font.
    def load_systemfont(self, name, size = 12):
        if not pygame.font.match_font(name):
            self._engine.console.warn(f"system font \"{name}\" does not exist!")
        self.__font = pygame.font.SysFont(name, size)

    # Load the default font.
    def load_default(self, size = 12):
        self.__font = pygame.font.Font(pygame.font.get_default_font(), size)

    # Get the current text buffer.
    def get_text(self):
        return self.__text
    
    # Set the text buffer.
    def set_text(self, text):
        self.__text = text
        self.__texture = None

    # Get the current x-alignment.
    def get_x_align(self):
        return self.__x_align

    # Set the x-alignment.
    def set_x_align(self, x_align):
        self.__x_align = x_align
        self.__texture = None
    
    # Get the current y-alignment.
    def get_y_align(self):
        return self.__y_align
    
    # Set the y-alignment.
    def set_y_align(self, y_align):
        self.__y_align = y_align
        self.__texture = None

    # Get whether this text is anti-aliased.
    def get_antialiased(self):
        return self.__antialiasing
    
    # Set the anti-aliasing of this text.
    def set_antialiased(self, toggle):
        self.__antialiasing = toggle
        self.__texture = None

    # Get the colour of this text.
    def get_colour(self):
        return self.__colour
    
    # Set the colour of this text.
    def set_colour(self, colour):
        self.__colour = colour
        self.__texture = None

    # Get whether this text is bold.
    def get_bold(self):
        return self.__bold
    
    # Set whether this text is bold.
    def set_bold(self, bold):
        self.__bold = bold
        self.__texture = None

    # Get whether this text is italic.
    def get_italic(self):
        return self.__italic
    
    # Set whether this text is italic.
    def set_italic(self, italic):
        self.__italic = italic
        self.__texture = None

    # Get whether this text is underlined.
    def get_underline(self):
        return self.__underline
    
    # Set whether this text is underlined.
    def set_underline(self, underline):
        self.__underline = underline
        self.__texture = None

    # Draw this text.
    def draw_text(self, screen):
        # Check that the font is valid.
        if not self.__font:
            return

        # Re-render the text surface if the texture is None.
        if not self.__texture:
            # Set the font properties.
            self.__font.set_bold(self.__bold)
            self.__font.set_italic(self.__italic)
            self.__font.set_underline(self.__underline)
            
            # Create a new transparent surface beforehand, which all text
            # surfaces will be blit onto.
            self.__texture = pygame.Surface((self._rect.width, self._rect.height), pygame.SRCALPHA)
            self.__texture.fill(pygame.Color(0, 0, 0, 0))

            # Split the text buffer into strings separated by newline, and
            # enumerate through each string.
            strings = self.__text.split("\n")
            for i, str in enumerate(strings):
                # Render this text buffer using the font.
                texture = self.__font.render(str, self.__antialiasing,
                                                    self.__colour)
                
                # Configure the alignment.
                if self.__x_align == X_LEFT:
                    x_offset = 0
                elif self.__x_align == X_CENTRE:
                    x_offset = max((self._rect.width - texture.get_width()) / 2, 0)
                else:
                    x_offset = max(self._rect.width - texture.get_width(), 0)
                if self.__y_align == Y_TOP:
                    y_offset = 0
                elif self.__y_align == Y_CENTRE:
                    y_offset = max((self._rect.height - texture.get_height()) / 2
                                   - (len(strings) - 1) * self.__font.get_linesize() / 2, 0)
                else:
                    y_offset = max(self._rect.height - texture.get_height()
                                   - (len(strings) - 1) * self.__font.get_linesize(), 0)
                y_offset += i * self.__font.get_linesize()
                
                # Blit the text surface onto the transparent surface.
                self.__texture.blit(texture, (x_offset, y_offset))

        # Render the text.
        screen.blit(self.__texture, self._rect)