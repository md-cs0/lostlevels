"""A basic logger implementation."""

import os
import datetime
import atexit
import __main__

import pygame

# ANSI escape code macros.
ANSI_ORANGE = "\033[38;5;208m"
ANSI_RED = "\033[38;5;9m"
ANSI_RESET = "\033[0m"

# Logger exception class to be thrown when a logger throws an error.
class LoggerException(Exception):
    pass

# A new logger instance will write to a named text document
# for each instance of this process in a logging folder, located
# in the current working directory.
class Logger():
    # Cache the date and time of this session.
    datetime = ""

    # Construct a new logger instance, with a specified name.
    def __init__(self, name, use_console = True):
        # Set the details of this logger.
        self.__name = name
        self.__use_console = use_console
        self.__buffer = [f"{__main__.__file__}:\n\n"]
        self.__closed = False

        # If it doesn't already exist, create a new folder in the
        # current working directory for logfiles.
        if not os.path.isdir("logging"):
            os.mkdir("logging")

        # Create a new directory for this session, if not done so.
        if Logger.datetime == "":
            now = datetime.datetime.now()
            Logger.datetime = now.strftime("%Y-%m-%d %H-%M-%S") # YYYY-MM-DD hh-mm-ss
            os.mkdir(f"logging/{Logger.datetime}")

        # Check if a logfile under this name already exists.
        filename = f"logging/{Logger.datetime}/{self.__name}.txt"
        if os.path.isfile(filename):
            raise FileExistsError(f"Logfile with name {self.__name} already exists!")

        # Create a new file for this logger.
        self.__file = open(filename, "w")

        # Create a function that will clean up this logger instance
        # (if still alive) on process exit.
        def cleanup():
            self.close()
        atexit.register(cleanup)

    # Write a standard log.
    def log(self, message):
        # Check if this logger is already closed.
        if self.__closed:
            return
        
        # Write a standard log to the buffer, and console if specified.
        time = datetime.datetime.now().strftime("[%Y-%m-%d %H-%M-%S]")
        self.__buffer.append(f"{time}: {message}\n")
        if self.__use_console:
            print(message)

    # Write a warning. This will print orange-coloured text
    # and prepend a *WARNING*.
    def warn(self, message):
        # Check if this logger is already closed.
        if self.__closed:
            return

        # Write a warning to the buffer, and console if specified.
        output = f"*WARNING* {message}"
        time = datetime.datetime.now().strftime("[%Y-%m-%d %H-%M-%S]")
        self.__buffer.append(f"{time}: {output}\n")
        if self.__use_console:
            print(f"{ANSI_ORANGE}{output}{ANSI_RESET}")

    # Write an error. This will print red-coloured tex, prepend
    # an *ERROR* and throw an exception. Use in critical-case
    # scenarios only!
    def error(self, message):
        # Check if this logger is already closed.
        if self.__closed:
            return
        
        # Shutdown Pygame, so that it doesn't freeze entirely.
        pygame.quit()

        # Write an error to the buffer, and console if specified.
        output = f"*ERROR* {message}"
        time = datetime.datetime.now().strftime("[%Y-%m-%d %H-%M-%S]")
        self.__buffer.append(f"{time}: {output}\n")
        if self.__use_console:
            print(f"{ANSI_RED}{output}{ANSI_RESET}")
            input() # Stall the program to force the user to respond.
        raise LoggerException(message) # Force the engine to stop.

    # Close this logger.
    def close(self):
        # Check if this logger is already closed.
        if self.__closed:
            return
        
        # Close the file and mark this logger as closed.
        self.__closed = True
        self.__file.write("".join(self.__buffer))
        self.__file.close()

# Execute this file directly for tests.
if __name__ == "__main__":
    # Create a new logger instance, and do some writing.
    test = Logger("test")
    test.log("hello world!")
    test.warn("hopefully, logging works!")

    # Test collision.
    try:
        collide = Logger("test")
    except FileExistsError:
        print("collision detection works!")

    # Create another two logger instances.
    test2 = Logger("test2", False)
    test3 = Logger("test3", False)
    test3.warn("Hello world!")

    # Error.
    test3.error("test!")