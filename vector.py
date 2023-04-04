from math import sin, cos, sqrt, pi


class Vector:
    """2D vector with arithmetic functionality"""

    def __init__(self, values=(0, 0)):
        if hasattr(values, '__iter__') and len(values) == 2:  # Maybe also type check to prevent strings eg "aa"
            self.x, self.y = values

    def __xor__(self, other):
        # Wedge product
        if isinstance(other, Vector):
            return self.x * other.get_y() - self.y * other.get_x()

    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Vector((self.x + other, self.y + other))
        elif isinstance(other, Vector):
            return Vector((self.x + other.get_x(), self.y + other.get_y()))

    def __sub__(self, other):
        if isinstance(other, (int, float)):
            return Vector((self.x - other, self.y - other))
        elif isinstance(other, Vector):
            return Vector((self.x - other.get_x(), self.y - other.get_y()))

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Vector((self.x * other, self.y * other))
        elif isinstance(other, Vector):
            return self.x * other.x + self.y * other.y

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return Vector((self.x / other, self.y / other))

    def __pow__(self, other):
        if other == 2:
            return self.x * self.y

    def __abs__(self):
        return self.mag()

    def __repr__(self):
        return str((self.x, self.y))

    def __iter__(self):
        yield self.x
        yield self.y

    def __getitem__(self, item):
        return [self.x, self.y][item]

    def __len__(self):
        return 2

    def __int__(self):
        return [int(self.x), int(self.y)]

    def __lt__(self, other):
        return self.y < other.y

    def __gt__(self, other):
        return self.y > other.y

    def __neg__(self):
        return Vector((-self.x, -self.y))

    def to_point(self):
        return int(self.x), int(self.y)

    def rotate90(self):
        return Vector((-self.y, self.x))

    def rotate(self, theta):
        # theta *= pi / 180
        x = self.x * cos(theta) - self.y * sin(theta)
        y = self.x * sin(theta) + self.y * cos(theta)
        return Vector((x, y))

    def rotate_ip(self, theta):
        # theta *= pi / 180
        tmp = self.x * cos(theta) - self.y * sin(theta)
        self.y = self.x * sin(theta) + self.y * cos(theta)
        self.x = tmp

    def transform(self, spaces):
        new = Vector((self.x, self.y))
        for space in spaces:
            if isinstance(space, VectorSpace):
                new.rotate_ip(space.direction)
                new += space.position
        return new

    def transform_inverse(self, spaces):
        new = Vector((self.x, self.y))
        for space in spaces[::-1]:
            if isinstance(space, VectorSpace):
                new -= space.position
                new.rotate_ip(-space.direction)
        return new

    def normalise(self):
        new = Vector((self.x, self.y))
        return new / abs(new)

    def mag(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def hat(self):
        return self / self.mag()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_int(self):
        return int(self.x), int(self.y)

    def copy(self):
        return Vector((self.x, self.y))


class VectorSpace:
    def __init__(self, position=None, direction=None):
        if position is None:
            position = (0, 0)
        if direction is None:
            direction = 0

        self.position = Vector(position)
        self.direction = direction

    def rotate(self, theta):
        self.direction += theta

    def translate(self, position):
        self.position += Vector(position)

    def __neg__(self):
        return VectorSpace(-self.position, -self.direction)
