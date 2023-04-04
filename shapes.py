from vector import Vector, VectorSpace
from math import pi
from abc import ABCMeta, abstractmethod
from constants import *


class Shape(metaclass=ABCMeta):
    """Abstract base class representing all shapes in the sim"""

    @abstractmethod
    def get_area(self):
        """returns the area of the shape"""
        return NotImplementedError

    @abstractmethod
    def get_barycenter(self):
        """returns the centre of mass of the shape"""
        return NotImplementedError

    @abstractmethod
    def contains_point(self, point):
        """checks if the shape contains a point"""
        return NotImplementedError

    @abstractmethod
    def get_normal(self, point):
        """get the surface normal of the shape at a particular point"""
        return NotImplementedError

    @abstractmethod
    def get_bounding_rect(self, space):
        """returns the smallest axis aligned bounding box containing the shape, clockwise from top-left-most point"""
        return NotImplementedError

    @abstractmethod
    def project(self, axis):
        """returns the upper and lower bounds of the shadow of the shape cast on a particular axis"""
        return NotImplementedError

    @abstractmethod
    def get_axis(self):
        """TBA"""
        return NotImplementedError


class Circle(Shape):
    def __init__(self, radius):
        """"""
        self.radius = radius
        self.area = pi * radius ** 2
        self.centroid = self.barycenter = Vector()

    def get_area(self):
        return self.area

    def get_barycenter(self):
        return self.barycenter

    def get_centroid(self):
        return self.centroid

    def get_normal(self, point):
        return (self.centroid - Vector(point)).normalise()

    def get_bounding_rect(self, space):
        return [-self.radius, -self.radius, self.radius, self.radius]

    def get_axis(self):
        return Vector((1, 0))

    def contains_point(self, point):
        return abs(self.centroid - Vector(point)) < self.radius

    def project(self, axis):
        return [-self.radius, self.radius]


class Polygon(Shape):
    def __init__(self, vertices: list[Vector]):
        """Takes a collection of points and initialises a convex polygon"""
        self.vertices = vertices
        self.vertices = self.make_convex()
        self.order = len(self.vertices)

        self.area = self.calc_area()
        self.triangles = self.triangulate()
        self.centroid = self.calc_centroid()
        self.barycenter = self.calc_barycenter()
        self.bounding_radius = self.calc_bounding_radius()
        self.axis = self.calc_axis()

    def make_convex(self):
        """Both makes polygon convex and normalises vertex list, starts on highest vertex and goes anticlockwise"""
        vertices = self.vertices
        convex_vertices = list()

        next_vertex = max(vertices)

        i = 0
        while True:
            convex_vertices.append(next_vertex)
            end_vertex = vertices[0]
            for vertex in vertices[1:]:
                if (convex_vertices[i] == end_vertex) or \
                        (vertex - convex_vertices[i]) ^ (end_vertex - convex_vertices[i]) > 0:
                    end_vertex = vertex

            next_vertex = end_vertex
            i += 1
            if next_vertex == convex_vertices[0]:
                break

        return convex_vertices

    def triangulate(self):
        """Updates """
        triangles = list()
        if self.order > 3:
            for i in range(len(self.vertices) - 2):
                triangles.append(Polygon([self.vertices[0],
                                          self.vertices[i + 1],
                                          self.vertices[i + 2]]))
        else:
            triangles = [self]

        return triangles

    def calc_area(self):
        area = 0
        n = len(self.vertices)
        for i in range(n):
            area += self.vertices[i] ^ self.vertices[(i + 1) % n]
        return area / 2

    def calc_centroid(self):
        return sum(self.vertices, Vector()) / self.order

    def calc_barycenter(self):
        if self.order == 3:
            return self.centroid

        barycenter = Vector()
        for triangle in self.triangles:
            barycenter += triangle.calc_barycenter() * triangle.area

        return barycenter / self.area

    def calc_axis(self):
        axis = []
        for i in range(self.order):
            edge = self.vertices[(i + 1) % self.order] - self.vertices[i]
            axis.append(edge.normalise().rotate90())
        return axis

    def contains_point(self, point):
        if self.order == 3:
            # Barycentric Technique (https://blackpawn.com/texts/pointinpoly/default.html)
            v0 = Vector(self.vertices[1]) - Vector(self.vertices[0])
            v1 = Vector(self.vertices[2]) - Vector(self.vertices[0])
            v2 = Vector(point) - Vector(self.vertices[0])

            u = ((v1 * v1) * (v2 * v0) - (v1 * v0) * (v2 * v1)) / ((v1 * v1) * (v0 * v0) - (v0 * v1) * (v1 * v0))
            v = ((v0 * v0) * (v2 * v1) - (v0 * v1) * (v2 * v0)) / ((v1 * v1) * (v0 * v0) - (v0 * v1) * (v1 * v0))

            return u >= 0 and v >= 0 and u + v <= 1

        for triangle in self.triangles:
            if triangle.contains_point(point):
                return True

        return False

    def calc_bounding_radius(self):
        maximum = abs(self.vertices[0] - self.barycenter)
        for vertex in self.vertices[1:]:
            d = abs(vertex - self.barycenter)
            if d > maximum:
                maximum = d

        return maximum

    def get_bounding_radius(self):
        return self.bounding_radius

    def get_normal(self, point):
        pass

    def get_area(self):
        return self.area

    def get_barycenter(self):
        return self.barycenter

    def get_bounding_rect(self, space):
        vertices = self.get_transformed_vertices([space])

        min_x = min(vertices, key=lambda v: v.get_x()).get_x()
        min_y = min(vertices, key=lambda v: v.get_y()).get_y()
        max_x = max(vertices, key=lambda v: v.get_x()).get_x()
        max_y = max(vertices, key=lambda v: v.get_y()).get_y()
        return [min_x - 3, min_y - 3, max_x + 4, max_y + 4]

    def get_bounding_rect_radius(self, space):
        min_x = (self.barycenter - self.bounding_radius + space.position).get_x()
        min_y = (self.barycenter - self.bounding_radius + space.position).get_y()
        max_x = (self.barycenter + self.bounding_radius + space.position).get_x()
        max_y = (self.barycenter + self.bounding_radius + space.position).get_y()
        return [min_x - 3, min_y - 3, max_x + 4, max_y + 4]

    def translate(self, vector):
        self.centroid += vector
        self.barycenter += vector
        self.vertices = [vertex + vector for vertex in self.vertices]
        self.bounding_radius = self.calc_bounding_radius()

    def get_vertices(self):
        return self.vertices

    def get_transformed_vertices(self, spaces):
        return [vertex.transform(spaces) for vertex in self.vertices]

    def get_axis(self):
        return self.axis

    def project(self, axis):
        """returns the upper and lower bounds of the shadow cast on a particular axis"""
        axis = axis.normalise()
        minimum = maximum = axis * self.vertices[0]
        for vertex in self.vertices:
            proj = axis * vertex
            if proj < minimum:
                minimum = proj
            elif proj > maximum:
                maximum = proj

        return minimum, maximum


class Collidable:
    def __init__(self, shape, density, drawer):
        self.high_priority = False
        self.drawer = drawer
        self.shape = shape
        self.density = density

        self.mass = shape.get_area() * self.density
        self.inertia = self.mass * self.shape.get_bounding_radius()**2 / 2

        self.position = Vector()
        self.orientation = 0

        self.linear_velocity = Vector()
        self.angular_velocity = 0

    def get_space(self):
        return VectorSpace(self.position, self.orientation)

    def resolve_impulse(self, impulse, position, normal):
        """adjusts object's linear and angular velocity based on impulse and location of impulse relative to
            center of mass"""
        self.linear_velocity += (normal * impulse) / self.mass
        self.angular_velocity += position * impulse ^ normal / self.inertia
        self.drawer.draw_vector(self.local_to_global(position), normal)

    def get_bounding_rect(self):
        return self.shape.get_bounding_rect(self.get_space())

    def update_body(self):
        self.position += self.linear_velocity
        self.orientation += self.angular_velocity

        # Basic method of keeping objects from escaping screen
        if self.position.x > SCREENWIDTH:
            self.linear_velocity.x = -abs(self.linear_velocity.x)
        elif self.position.x < 0:
            self.linear_velocity.x = abs(self.linear_velocity.x)
        elif self.position.y > SCREENHEIGHT:
            self.linear_velocity.y = -abs(self.linear_velocity.y)
        elif self.position.y < 0:
            self.linear_velocity.y = abs(self.linear_velocity.y)

    def get_point_velocity(self, point):
        # self.drawer.draw_vector(Vector(point), self.linear_velocity + Vector(point).rotate(90+self.orientation))
        return self.linear_velocity + Vector(point).rotate(90 + self.orientation) * self.angular_velocity

    def global_to_local(self, point):
        return point.transform_inverse([self.get_space()])

    def local_to_global(self, point):
        return point.transform([self.get_space()])

    def get_linear_velocity(self):
        return self.linear_velocity

    def get_angular_velocity(self):
        return self.angular_velocity

    def get_mass(self):
        return self.mass

    def get_inertia(self):
        return self.inertia

    def project(self, axis):
        axis = axis.normalise()
        minimum, maximum = self.shape.project(axis.rotate(-self.orientation))
        projected_position = axis * self.position
        minimum += projected_position
        maximum += projected_position
        return minimum, maximum

    def set_high_priority(self):
        self.high_priority = True

    def is_high_priority(self):
        return self.high_priority


def main():
    s = Polygon([Vector((0, 1)), Vector((1, 0)), Vector((-1, 0))])
    p = Collidable(s, 1, None)
    v = Vector((1, 0))
    for i in range(360):
        v = v.rotate(1)
        a, b = p.project(v)
        if not a < b:
            print(a, b)


if __name__ == "__main__":
    main()

# interesting note:
# incorrectly remembering gift-wrapping algorithm lead to spiral-making algorithm
# def make_convex(self):
#     vertices = self.vertices
#     convexVertices = list()
#
#     maximum = max(vertices)
#     convexVertices.append(maximum)
#     vertices.remove(maximum)
#
#     i = 0
#     # endVertex = vertices[0]
#     while vertices:
#         endVertex = vertices[0]
#         for vertex in vertices[1:]:
#             # print(vertex)
#             if (vertex - convexVertices[i]) ^ (endVertex - convexVertices[i]) < 0:
#                 endVertex = vertex
#
#         convexVertices.append(endVertex)
#         vertices.remove(endVertex)
#         i += 1
#     # print("done")
#     self.vertices = convexVertices
