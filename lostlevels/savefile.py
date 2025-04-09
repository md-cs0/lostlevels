"""Save file implementation for LLSV .sav files."""

import os
import ctypes

from . import levelinfo

# Error states. 
LLSV_OK         = 0 # Save file instantiated successfully.
LLSV_NOTEXISTS  = 1 # The save file path is invalid.
LLSV_MAGIC      = 2 # The magic of the save file is wrong.
LLSV_CORRUPT    = 3 # Save file data is corrupted due to missing data.

# LLSV magic.
LLSV_MAGIC      = 0x56534C4C # LLSV

# LLSV header.
class LLSVHeader(ctypes.Structure):
    # Declare the fields.
    _fields_ = [("m_iMagic", ctypes.c_int),
                ("m_au8Flags", ctypes.c_ubyte * 16),
                ("m_sLives", ctypes.c_short),
                ("m_sCoins", ctypes.c_short),
                ("m_uScore", ctypes.c_uint),
                ("m_ePowerup", ctypes.c_ubyte),
                ("m_u8NumWorlds", ctypes.c_ubyte)]
    
    # Set default values to the fields.
    def __init__(self):
        self.m_iMagic = LLSV_MAGIC
        self.m_sLives = 3
        self.m_u8NumWorlds = levelinfo.NUM_WORLDS

# Save file class.
class LLSV():
    # Create a new save file.
    def __init__(self, name):
        self.name = name
        self.header = LLSVHeader()
        self.currentlevel = [1, 1, 1]
    
    # Read from an existing save file.
    def read(self, savedir = ""):
        # Validate whether the save file exists.
        path = os.path.join(savedir, self.name + ".sav")
        if not os.path.exists(path):
            return LLSV_NOTEXISTS
        
        # Read the save file.
        with open(path, "rb") as file:
            # Read the header and check whether we read the header fully.
            if file.readinto(self.header) != ctypes.sizeof(self.header):
                return LLSV_CORRUPT
            
            # Verify the magic.
            if self.header.m_iMagic != LLSV_MAGIC:
                return LLSV_MAGIC
            
            # Read until the number of worlds is reached.
            self.currentlevel = []
            for i in range(0, self.header.m_u8NumWorlds):
                level = file.read(1)
                if len(level) == 0:
                    return LLSV_CORRUPT
                self.currentlevel.append(level[0])

        # Return OK.
        return LLSV_OK
    
    # Write to a save file.
    def write(self, savedir = ""):
        # Create the save file.
        path = os.path.join(savedir, self.name + ".sav")
        with open(path, "wb") as file:
            # Write the header.
            file.write(self.header)

            # Write the current level for each world.
            for level in self.currentlevel:
                file.write(level.to_bytes(1, "little"))