"""The root UI element class, which all default UI elements
derive from."""

import pygame
from ..event import Event
from .udim2 import UDim2

# UI element layer types.
LAYER_BACKGROUND    = 0 # This entity is in the background layer.
LAYER_FOREGROUND    = 1 # This entity is in the foreground layer.

# The root element class.
class Element():
    # Construct a new UI element.
    def __init__(self, engine, classname = "element"):
        # Set some basic identifiable attributes for this element.
        self.__classname = classname
        self.__events = dict()
        self._rect = pygame.Rect(0, 0, 0, 0)
        self._engine = engine
        self.enabled = False

        # UI element description.
        self.__position = UDim2(0, 0, 0, 0)
        self.__size = UDim2(0, 0, 0, 0)
        self.layer = LAYER_FOREGROUND

        # Create a few crucial events.
        self.set_event(Event("draw", placeholder))
        self.set_event(Event("selected", placeholder))

        # Engine linked list implementation.
        self.prev = None
        self.next = None

    # Get the class name of this element.
    def get_class(self):
        return self.__classname
    
    # Get the position of this element.
    def get_position(self):
        return self.__position
    
    # Set the position of this element.
    def set_position(self, udim2):
        self.__position = udim2
        self._rect.left = self._engine.game_width.get() * udim2.x.scale + udim2.x.offset
        self._rect.top = self._engine.game_height.get() * udim2.y.scale + udim2.y.offset

    # Get the size of this element.
    def get_size(self):
        return self.__size
    
    # Set the size of this element.
    def set_size(self, udim2):
        self.__size = udim2
        self._rect.width = self._engine.game_width.get() * udim2.x.scale + udim2.x.offset
        self._rect.height = self._engine.game_height.get() * udim2.y.scale + udim2.y.offset

    # Retrieve an event from this element.
    def get_event(self, name):
        if name not in self.__events:
            self._engine.console.warn(f"Entity {self.__classname}: could not find event \"{name}\"")
            return None
        return self.__events[name]

    # Set an event to this element.
    def set_event(self, event):
        self.__events[event.get_name()] = event

    # Invoke an event.
    def invoke_event(self, name, *args):
        if (event := self.get_event(name)) == None:
            return None
        return event.invoke(self, *args)

    # Handle element deletion by unlinking this element from its neighbouring elements.
    def unlink(self):
        if self.prev:
            self.prev.next = self.next
        if self.next:
            self.next.prev = self.prev

# Placeholder function.
def placeholder(sprite, *args):
    #sprite._engine.console.log(f"UI element {sprite.get_class()}: engine/ui/element.py placeholder function called!")
    pass

# Define what should be imported from this module.
__all__ = ["Element", "LAYER_BACKGROUND", "LAYER_FOREGROUND"] 