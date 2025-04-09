"""A basic module for creating audio instances."""

import os
import pygame
import numpy

# Cached sound information.
cached_sounds = dict()

# The root sound class.
class Sound():
    # Loaded sound information.
    cached_sample_rate = 0
    num_channels = 0

    # Construct a new sound instance.
    def __init__(self, engine):
        # Create a few public properties for manipulating this
        # sound instance.
        self.volume = 0.5
        self.speed = 1.0

        # Track whether this sound instance loops or not.
        self.__looping = False
        
        # Hold a buffer of all the audio samples and the internal
        # sound instance.
        self.buffer = None
        self.__sound = None

        # Bind the engine instance to this sound instance.
        self.__engine = engine

    # Load an existing sound file.
    def load(self, path):
        # Fallback function, should the sound file be invalid.
        def fallback():
            nonlocal self, path
            self.__engine.console.warn(f"sound path \"{path}\" is invalid")
            self.buffer = self.__sound = None
            
        # Check whether the sound buffer is already cached.
        abspath = os.path.abspath(path)
        if abspath in cached_sounds:
            self.buffer = cached_sounds[abspath]
        else:
            # Check if the path for the sheet exists.
            if not os.path.isfile(path):
                fallback()
                return
            
            # Attempt to load the audio file.
            try:
                sound = pygame.mixer.Sound(abspath)
                self.buffer = cached_sounds[abspath] = pygame.sndarray.array(sound)
            except pygame.error:
                fallback()
                return
            
    # Check if this sound file has loaded.
    def loaded(self):
        return isinstance(self.buffer, numpy.ndarray)

    # Play the sound file.
    def play(self, loop = False):
        # Check if the audio buffer is loaded, or if we are already playing.
        if not self.loaded() or self.playing():
            return
        
        # If the playback speed is any value besides 1, copy the sound buffer
        # and remove/duplicate samples accordingly.
        buffer = self.buffer
        if self.speed != 1.0:
            indices = numpy.arange(0, len(buffer), self.speed).astype(int)
            buffer = buffer[indices[indices < len(buffer)]]

        # Create the sound instance.
        self.__sound = pygame.mixer.Sound(buffer)
        self.__sound.set_volume(self.volume)
        self.__sound.play(-1 if loop else 0)
        
        # Set whether this sound instance is looping or not.
        self.__looping = loop

    # Stop playing this sound file.
    def stop(self):
        # Check whether are actually playing.
        if not self.playing():
            return
        
        # Stop playing.
        self.__sound.stop()
        self.__sound = None
        self.__looping = False

    # Repeat this sound file.
    def repeat(self, loop = False):
        self.stop()
        self.play(loop)

    # Is this sound file playing?
    def playing(self):
        # If the sound instance is valid, return true if it is playing,
        # otherwise remove it if it is not playing in any channels.
        if self.__sound:
            if self.__sound.get_num_channels() > 0:
                return True
            else:
                self.__sound = None
                self.__looping = False

        # The song instance is invalid, return false.
        return False
    
    # Is this sound file looping?
    def looping(self):
        return self.__looping
    
    # Get the length of this sound file.
    def __len__(self):
        return len(self.buffer) / Sound.cached_sample_rate