"""Events can be used to transmit signals, with a primary function
and any additional detours being called."""

# An event, which can be invoked, detoured, and therefore superceded.
# Detours must return either:
# - Event.DETOUR_CONTINUE
# - a tuple: (Event.DETOUR_*, return_value)
# Detours must accept the following parameters: eventName, returnValue, ...
class Event():
    # Detour return types.
    DETOUR_CONTINUE     = 0 # Continue as per normal.
    DETOUR_OVERRIDE     = 1 # Override the return value.
    DETOUR_SUPERSEDE    = 2 # Immediately halt execution and use the newly-specified return value.

    # Create a new event.
    def __init__(self, name, func):
        self.__name = name
        self.__func = func
        self.__pre = []       # Pre-call detours.
        self.__post = []      # Post-call detours.

    # Get the name of this event.
    def get_name(self):
        return self.__name
    
    # Replace the current function to be invoked with a new one.
    def set_func(self, func):
        self.__func = func
    
    # Detour this event with a new function.
    def hook(self, function, post = False):
        if post:
            if function in self.__post:
                return
            self.__post.append(function)
        else:
            if function in self.__pre:
                return
            self.__pre.append(function)

    # Remove a detoured function from this event.
    def remove_hook(self, function, post = False):
        if post and function in self.__post:
            self.__post.remove(function)
        elif function in self.__pre:
            self.__pre.remove(function)

    # Invoke this event.
    def invoke(self, *args):
        # Configure the return value at the start.
        returnValue = None
        overrided = False

        # Call any pre-call detours.
        for pre in self.__pre:
            result = pre(args[0], self.__name, returnValue, *args[1:])
            if result != Event.DETOUR_CONTINUE:
                if result[0] == Event.DETOUR_SUPERSEDE:
                    return result[1]
                elif result[0] == Event.DETOUR_OVERRIDE:
                    returnValue = result[1]
                    overrided = True

        # Call the original function.
        expectedReturn = self.__func(*args)
        if not overrided:
            returnValue = expectedReturn
        
        # Call any post-call detours.
        for post in self.__post:
            result = post(args[0], self.__name, returnValue, *args[1:])
            if result != Event.DETOUR_CONTINUE:
                if result[0] == Event.DETOUR_SUPERSEDE:
                    return result[1]
                elif result[0] == Event.DETOUR_OVERRIDE:
                    returnValue = result[1]
        
        # Return the return value.
        return returnValue