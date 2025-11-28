"""Demo file type for recording Lost Levels gameplay. The file format is
named Lost Levels Demo (LLDE) and the .dem file extension is used."""

import os
import ctypes

from . import savefile

# Error states. 
LLDE_OK                 = 0             # Demo file instantiated successfully.
LLDE_NOTEXISTS          = 1             # The demo file path is invalid.
LLDE_MAGIC              = 2             # The magic of the demo file is wrong.
LLDE_CORRUPT            = 3             # Demo file data is corrupted due to missing data.
LLDE_WRONGVER           = 4             # The given demo file version number does not match what the game expects.

# LLDE magic.
LLDE_MAGIC              = 0x45444C4C    # LLDE

# Current LLDE demo file version number.
LLDE_DEMOVER            = 1

# Object types.
LLDE_OBJECT_BASE        = 0
LLDE_OBJECT_INPUT       = 1
LLDE_OBJECT_EVENT       = 2
LLDE_OBJECT_CHECKPOINT  = 3
LLDE_OBJECT_GAMECALL    = 4

# Demo file base object. Each object is timestamped.
class LLDEObject(ctypes.Structure):
    # Declare the fields.
    _fields_ = [("m_eObjectType", ctypes.c_uint8),
                ("m_u64Tick", ctypes.c_uint64)]

# Input object. This stores the key enum and whether it was a keydown or keyup
# event.
class LLDEInputObject(LLDEObject):
    # Declare the fields.
    _fields_ = [("m_eKey", ctypes.c_int),
                ("m_bKeyDown", ctypes.c_bool)]
    
    # Set default values to the fields.
    def __init__(self):
        super().__init__()
        self.m_eObjectType = LLDE_OBJECT_INPUT

# Event object. This is used to invoke a given event on a unique entity.
class LLDEEventObject(LLDEObject):
    # Declare the fields.
    _fields_ = [("m_szEntityName", ctypes.c_char * 128),
                ("m_szEventName", ctypes.c_char * 128)]
    
    # Set default values to the fields.
    def __init__(self):
        super().__init__()
        self.m_eObjectType = LLDE_OBJECT_EVENT

# Checkpoint object. This is used to set checkpoint data upon starting a demo.
class LLDECheckpointObject(LLDEObject):
    # Declare the fields.
    _fields_ = [("m_flTimeLimit", ctypes.c_float),
                ("m_flOffsetX", ctypes.c_float),
                ("m_flOffsetY", ctypes.c_float)]
    
    # Set default values to the fields.
    def __init__(self):
        super().__init__()
        self.m_eObjectType = LLDE_OBJECT_CHECKPOINT

# Game call object. This is preferred over timestamping calls to LostLevels
# methods.
class LLDEGameCallObject(LLDEObject):
    # Declare the fields.
    _fields_ = [("m_szMethodName", ctypes.c_char * 32)]
    
    # Set default values to the fields.
    def __init__(self):
        super().__init__()
        self.m_eObjectType = LLDE_OBJECT_GAMECALL

# LLDE header.
class LLDEHeader(ctypes.Structure):
    # Declare the fields.
    _fields_ = [("m_iMagic", ctypes.c_int),
                ("m_u8Version", ctypes.c_ubyte),
                ("m_u8World", ctypes.c_ubyte),
                ("m_u8Level", ctypes.c_ubyte),
                ("m_cObjects", ctypes.c_size_t),
                ("m_flMaxFPS", ctypes.c_float),
                ("m_LLSVHeader", savefile.LLSVHeader)]
    
    # Set default values to the fields.
    def __init__(self):
        self.m_iMagic = LLDE_MAGIC
        self.m_LLSVHeader = savefile.LLSVHeader()

# Demo file class.
class LLDE():
    # Link object types to their respective classes.
    __object_class = {
        LLDE_OBJECT_BASE:       LLDEObject,
        LLDE_OBJECT_INPUT:      LLDEInputObject,
        LLDE_OBJECT_EVENT:      LLDEEventObject,
        LLDE_OBJECT_CHECKPOINT: LLDECheckpointObject,
        LLDE_OBJECT_GAMECALL:   LLDEGameCallObject
    }

    # Create a new demo file.
    def __init__(self, name):
        # Configure basic demo properties.
        self.name = name
        self.header = LLDEHeader()
        
        # LLDE demo files will also hold save data, in order to accurately capture
        # the recording player's current save data.
        self.savecopy = savefile.LLSV("INTERIM DEMO SAVEFILE")

        # Store an array of demo file objects.
        self.__objects = []

        # Is this demo recording the player's gameplay?
        self.recording = False

        # What is the first game tick for this demo file?
        self.first_tick = 0

    # Read from an existing demo file.
    def read(self, demodir = ""):
        # Validate whether the demo file exists.
        path = os.path.join(demodir, self.name + ".dem")
        if not os.path.exists(path):
            return LLDE_NOTEXISTS
        
        # Read the demo file.
        with open(path, "rb") as file:
            # Read the header and check whether we read the header fully.
            if file.readinto(self.header) != ctypes.sizeof(self.header):
                return LLDE_CORRUPT
            
            # Verify the magic.
            if self.header.m_iMagic != LLDE_MAGIC:
                return LLDE_MAGIC

            # Enqueue each object into the objects queue.
            for i in range(0, self.header.m_cObjects):
                # Get the type of the current object to read.
                pos = file.tell()
                obj_type = file.read(1)[0]
                file.seek(pos)

                # Read the entire object and validate its integrity.
                if obj_type not in LLDE.__object_class:
                    return LLDE_CORRUPT
                obj = LLDE.__object_class[obj_type]()
                if file.readinto(obj) != ctypes.sizeof(obj):
                    return LLDE_CORRUPT
                self.enqueue(obj)
            
    # Write to a demo file.
    def write(self, demodir = ""):
        # Write the number of objects to the header.
        self.header.m_cObjects = len(self.__objects)

        # Create the demo file.
        path = os.path.join(demodir, self.name + ".dem")
        with open(path, "wb") as file:
            # Write the header.
            file.write(self.header)

            # Write alll the demo objects.
            for obj in self.__objects:
                file.write(obj)

    # Enqueue a new object.
    def enqueue(self, obj):
        self.__objects.append(obj)

    # Dequeue an object from the objects queue.
    def dequeue(self):
        if len(self.__objects) == 0:
            return None
        return self.__objects.pop(0)
    
    # Peek the latest object in the objects queue.
    def peek(self):
        if len(self.__objects) == 0:
            return None
        return self.__objects[0]