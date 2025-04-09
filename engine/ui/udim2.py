"""A 2-dimensional struct representing a UI element's scale and offset."""

# 2-dimensional co-ordinates of a UI element.
class UDim2():
    # Individual co-ordinate class.
    class Coord():
        # Construct a new co-ordinate.
        def __init__(self, scale, offset):
            self.scale = scale
            self.offset = offset

    # Construct a new UDim2.
    def __init__(self, x_scale, x_offset, y_scale, y_offset):
        self.x = UDim2.Coord(x_scale, x_offset)
        self.y = UDim2.Coord(y_scale, y_offset)

    # Addition.
    def __add__(self, other):
        return UDim2(self.x.scale + other.y.scale,
                     self.x.offset + other.x.offset,
                     self.y.scale + other.y.scale,
                     self.y.offset + other.y.offset)

    # Subtraction.
    def __sub__(self, other):
        return UDim2(self.x.scale - other.y.scale,
                     self.x.offset - other.x.offset,
                     self.y.scale - other.y.scale,
                     self.y.offset - other.y.offset)
    
    # Multiplication.
    def __mul__(self, other):
        return UDim2(self.x.scale * other.y.scale,
                     self.x.offset * other.x.offset,
                     self.y.scale * other.y.scale,
                     self.y.offset * other.y.offset)
    
    # Division.
    def __div__(self, other):
        return UDim2(self.x.scale / other.y.scale,
                     self.x.offset / other.x.offset,
                     self.y.scale / other.y.scale,
                     self.y.offset / other.y.offset)

    # Negation.
    def __neg__(self):
        return UDim2(-self.x.scale,
                     -self.x.offset,
                     -self.y.scale,
                     -self.y.offset)
    
    # Unary positive.
    def __pos__(self):
        return UDim2.new(self.x.scale,
                         self.x.offset,
                         self.y.scale,
                         self.y.offset)
    
    # Check if this is equal to the other UDim2.
    def __eq__(self, other):
        return (self.x.scale == other.x.scale
                and self.x.offset == other.x.offset
                and self.y.scale == other.y.scale
                and self.y.offset == other.y.offset)
    
    # Check if this is not equal to the other UDim2.
    def __ne__(self, other):
        return (self.x.scale != other.x.scale
                or self.x.offset != other.x.offset
                or self.y.scale != other.y.scale
                or self.y.offset != other.y.offset)