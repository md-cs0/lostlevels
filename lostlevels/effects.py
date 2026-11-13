"""A bunch of sample functions for creating visual effects."""

import pygame
import engine

# Create a flash bang effect that gradually fades.
def create_flash_bang(eng, 
                      amount_faded_per_tick = 3, 
                      delay_before_fade_out = 0.25,
                      time_per_tick = 0.05):
    # Flash bang: gradually fade out and disappear after some time.
    def fade_frame(self):
        # If the frame has already been deleted, finish early.
        if self.deleted:
            return

        # Gradually fade out the frame.
        colour = self.get_colour()
        if colour.a == 0:
            eng.delete_ui_element(self)
        else:
            self.set_colour(pygame.Color(255, 255, 255, max(0, colour.a - amount_faded_per_tick)))
            eng.create_timer(fade_frame, time_per_tick, self)

    # Create the flash bang visual.
    frame = eng.create_ui_element_by_class("frame")
    frame.set_size(engine.ui.UDim2(1, 0, 1, 0))
    frame.set_colour(pygame.Color(255, 255, 255, 255))
    frame.enabled = True
    eng.create_timer(fade_frame, delay_before_fade_out, frame)

    # Return the flash bang visual.
    return frame

# Create a fade-in white screen effect.
def create_fade_in_screen(eng, fade_in_per_tick = 3, time_per_tick = 0.05):
    # Fade-ni: gradually in.
    def fade_frame(self):
        colour = self.get_colour()
        self.set_colour(pygame.Color(255, 255, 255, min(255, colour.a + fade_in_per_tick)))
        eng.create_timer(fade_frame, time_per_tick, self)

    # Create the fade-in visual.
    frame = eng.create_ui_element_by_class("frame")
    frame.set_size(engine.ui.UDim2(1, 0, 1, 0))
    frame.set_colour(pygame.Color(255, 255, 255, 0))
    frame.enabled = True
    eng.create_timer(fade_frame, time_per_tick, frame)

    # Return the fade-in visual.
    return frame