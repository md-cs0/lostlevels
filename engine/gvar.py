"""Game variable (can be defined in either the engine or
game code), which can contain values shared across the
entire game."""

# Game variable flags.
GVAR_PROGRAMONLY = (1 << 0) # This game variable can only be modified programmatically.

# Game variable class.
class GameVar():
    # Construct a new game variable.
    def __init__(self, name, value, description = "", flags = 0, min = None, max = None):
        # Instantiate a new game variable.
        self.__name = name
        self.__value = value
        self.__description = description
        self.__min = min
        self.__max = max
        self.flags = flags
        
        # Set the default value of this game variable.
        # This will also clamp the value, if defined.
        self.__default = self.set(value)

    # Retrieve the value of this game variable.
    def get(self):
        return self.__value

    # Set the value of this game variable.
    def set(self, value):
        # Verify the type.
        if not isinstance(value, type(self.__value)):
            raise TypeError(f"Type error in game variable {self.__name}: "      \
                            "type \"{type(self.__value).__name__}\" expected "  \
                            "but got \"{type(value).__name__}\" instead.")
        
        # Set the value and clamp it, if defined.
        self.__value = value
        if self.__min != None and self.__value < self.__min:
            self.__value = self.__min
        elif self.__max != None and self.__value > self.__max:
            self.__value = self.__max
        return self.__value
    
    # Reset this game variable back to its default value
    def reset(self):
        self.__value = self.__default

    # Retrieve the default value of this game variable.
    def get_default(self):
        return self.__default
    
    # Retrieve the minimum value of this game variable.
    def get_min(self):
        return self.__min
    
    # Set the minimum value of this game variable.
    def set_min(self, min):
        self.__min = min
        self.set(self.__value)

    # Retrieve the maximum value of this game variable.
    def get_max(self):
        return self.__max
    
    # Set the maximum value of this game variable.
    def set_max(self, max):
        self.__max = max
        self.set(self.__value)

    # Retrieve the string representation of this game variable.
    def __str__(self):
        # Configure the basic output buffer for this game variable.
        output = f"\"{self.__name}\" = \"{self.__value}\""
        if self.__value != self.__default:
            output += f" ( def. \"{self.__default}\" )"
        if self.__min != None:
            output += f" min. {self.__min}"
        if self.__max != None:
            output += f" max. {self.__max}"
        
        # Read each flag and append it to the output buffer.
        if self.flags:
            output += "\n "
            if self.flags & GVAR_PROGRAMONLY:
                output += "programonly "
        
        # Append the description to the output buffer, if desired.
        if self.__description != "":
            output += f"\n - {self.__description}"
        
        # Return the output buffer.
        return output