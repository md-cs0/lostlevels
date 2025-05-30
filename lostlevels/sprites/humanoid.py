"""The root class that will be shared amongst "living" entities."""

# The humanoid class. To prevent collision with inheritance,
# it will not inherit from Sprite by default.
class Humanoid():
    # Construct a new humanoid.
    def __init__(self):
        self.alive = True
        self.weapon = None