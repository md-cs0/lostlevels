"""A bunch of sample functions for creating visual effects."""

import pygame
import engine

# Create a flash bang effect that gradually fades.
def create_flash_bang(eng, amount_faded_per_tick = 3):
    # Flash bang: gradually fade out and disappear after some time.
    def fade_frame(self):
        colour = self.get_colour()
        if colour.a == 0:
            eng.delete_ui_element(self)
        else:
            self.set_colour(pygame.Color(255, 255, 255, max(0, colour.a - amount_faded_per_tick)))
            eng.create_timer(fade_frame, 1 / 20, self)

    # Create the flash bang visual.
    frame = eng.create_ui_element_by_class("frame")
    frame.set_size(engine.ui.UDim2(1, 0, 1, 0))
    frame.set_colour(pygame.Color(255, 255, 255, 255))
    frame.enabled = True
    eng.create_timer(fade_frame, 0.25, frame)