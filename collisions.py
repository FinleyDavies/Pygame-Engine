import shapes
from shapes import *
from constants import *
from vector import Vector
import time


class EndPoint:
    """Represents an endpoint of a collidable object that has been projected onto an axis"""

    def __init__(self, owner: Collidable, projection_normal: Vector, is_end: bool):
        self.owner = owner
        self.projection_normal = projection_normal
        self.is_end = is_end
        self.value = None

    def update_value(self):
        if not self.is_end:
            if self.projection_normal == Vector((0, 1)):  # X-axis projection
                pass
            elif self.projection_normal == Vector((1, 0)):  # Y-axis projection
                pass
            else:
                raise NotImplementedError("Projection onto non-orthogonal axis not yet supported")

    def __gt__(self, other):
        return self.value > other.value

    def __lt__(self, other):
        return other.value > self.value


class SweepPrune:
    def __init__(self, collidables):
        self.endpointsX = []
        self.endpointsY = []
        self.overlapsX = set()
        self.overlapsY = set()
        for body in collidables:
            self.endpointsX.append(EndPoint(body, Vector((0, 1)), False))
            self.endpointsX.append(EndPoint(body, Vector((0, 1)), True))
            self.endpointsY.append(EndPoint(body, Vector((1, 0)), False))
            self.endpointsY.append(EndPoint(body, Vector((1, 0)), True))

        self.update_values()

    def update_values(self):
        for endpoint in self.endpointsX:
            index = 0 if not endpoint.is_end else 2
            endpoint.value = endpoint.owner.get_bounding_rect()[index]

        for endpoint in self.endpointsY:
            index = 1 if not endpoint.is_end else 3
            endpoint.value = endpoint.owner.get_bounding_rect()[index]

    @staticmethod
    def detect_overlaps(endpoints, overlaps):
        for i in range(len(endpoints)):
            j = i

            while j > 0 and endpoints[j - 1] > endpoints[j]:
                if endpoints[j - 1].is_end != endpoints[j].is_end:
                    if endpoints[j - 1].is_end:
                        overlaps.add(frozenset({endpoints[j].owner,
                                         endpoints[j - 1].owner}))
                    else:
                        overlaps.remove(frozenset({endpoints[j].owner,
                                         endpoints[j - 1].owner}))
                endpoints[j], endpoints[j - 1] = endpoints[j - 1], endpoints[j]
                j = j - 1

        return overlaps

    def detect_overlaps_x(self):
        self.overlapsX = self.detect_overlaps(self.endpointsX, self.overlapsX)

    def detect_overlaps_y(self):
        self.overlapsY = self.detect_overlaps(self.endpointsY, self.overlapsY)

    def get_broad_pairs(self):
        self.detect_overlaps_x()
        self.detect_overlaps_y()

        return list(self.overlapsX.intersection(self.overlapsY))


class CollisionHandler:
    def __init__(self):
        pass

    def find_minimum_push_vector(self, object1, object2):

        def is_overlap(interval1, interval2):
            a, b = interval1
            c, d = interval2
            return a <= d and c <= b

        push_vector = Vector((1000, 1000))
        for axis in object1.shape.get_axis():
            axis = axis.rotate(object1.orientation)
            interval1 = object2.project(axis)
            interval2 = object1.project(axis)
            if not is_overlap(interval1, interval2):
                return Vector()
            v = axis * (interval2[0] - interval1[1])
            if abs(v) < abs(push_vector):
                push_vector = -v

        for axis in object2.shape.get_axis():
            axis = axis.rotate(object2.orientation)
            interval1 = object1.project(axis)
            interval2 = object2.project(axis)
            if not is_overlap(interval1, interval2):
                return Vector()
            v = axis * (interval2[0] - interval1[1])
            if abs(v) < abs(push_vector):
                push_vector = v
        push_vector *= 1.05

        # print("overlap",push_vector)
        # print(object1.mass, object2.mass)
        if object1.is_high_priority() and not object2.is_high_priority():
            object2.position -= push_vector
        elif object2.is_high_priority() and not object1.is_high_priority():
            object1.position += push_vector
        else:
            object1.position += push_vector / 2
            object2.position -= push_vector / 2
        #   else evaluate collisions based on the mass of the two objects

    def check_vertex_vertex(self, vertex1, vertex2, tolerance=None):
        if tolerance is None:
            tolerance = COLLISION_TOLERANCE

        normal = None
        if abs(vertex2 - vertex1) < tolerance:
            normal = (vertex2 - vertex1).normalise()

        return normal

    def check_vertex_edge(self, vertex, edge1, edge2, tolerance=None):
        if tolerance is None:
            tolerance = COLLISION_TOLERANCE

        normal = None
        edge = edge2 - edge1
        u = edge.normalise()
        p = vertex - edge1

        projection = u * (p * u)

        if abs(p ^ u) < tolerance and 0 < p * p < edge * p:
            normal = u.rotate(90)

        return normal

    def apply_impulse(self, object1, object2, normals):
        position = Vector()
        normal = Vector()
        for n in normals:
            position += n[0]
            normal += n[1]
        # position = (position/len(normals))
        # normal = (normal/len(normals)).normalise()
        normal = normals[0][1]
        position = normals[0][0]
        ##        relative_norm_vel = normal/abs(normal) * (object1.linear_velocity - object2.linear_velocity)
        ##        normal /= abs(normal)
        ##        numerator = -2*relative_norm_vel
        ##        denominator = normal * normal * (object1.mass + object2.mass)/(object1.mass * object2.mass)
        ##        impulse = numerator/denominator
        ##        object1.linear_velocity += normal * impulse/object1.mass
        ##        object2.linear_velocity -= normal * impulse/object2.mass
        ##
        ##        return 0

        local_position1 = object1.global_to_local(position)
        local_position2 = object2.global_to_local(position)

        relative_velocity = object2.get_point_velocity(local_position2) - \
                            object1.get_point_velocity(local_position1)
        print(relative_velocity)
        # print(object2.get_point_velocity(local_position2),
        #      object1.get_point_velocity(local_position1))
        # print(relative_velocity)
        relative_norm_vel = relative_velocity * normal
        print(relative_velocity)
        # print(relative_norm_vel)

        if relative_norm_vel < 0:
            numerator = -(1 + COEFFICIENT_RESTITUTION) * relative_norm_vel
            inverse_mass_sum = 1 / object1.get_mass() + 1 / object2.get_mass()
            normal_moment1 = (normal * (local_position1 ^ normal) ^ local_position1) / object1.get_inertia()
            normal_moment2 = (normal * (local_position2 ^ normal) ^ local_position2) / object2.get_inertia()
            impulse = numerator / (inverse_mass_sum + normal_moment1 + normal_moment2)
            object1.resolve_impulse(impulse, local_position1, normal)
            object2.resolve_impulse(-impulse, local_position2, normal)

    def handle_poly_poly(self, poly1, poly2):
        point_normals = list()
        verts1 = poly1.shape.get_transformed_vertices([poly1.get_space()])
        verts2 = poly2.shape.get_transformed_vertices([poly2.get_space()])

        # Find vertex-vertex collision points and normals
        for v1 in verts1:
            for v2 in verts2:
                normal = self.check_vertex_vertex(v1, v2)
                if normal is not None:
                    point_normals.append([v1, normal])

        for i in range(len(verts1)):
            edge1 = verts1[i]
            edge2 = verts1[(i + 1) % len(verts1)]
            for vertex in verts2:
                normal = self.check_vertex_edge(vertex, edge1, edge2)
                if normal is not None:
                    point_normals.append([vertex, -normal])

        for i in range(len(verts2)):
            edge1 = verts2[i]
            edge2 = verts2[(i + 1) % len(verts2)]
            for vertex in verts1:
                normal = self.check_vertex_edge(vertex, edge1, edge2)
                if normal is not None:
                    point_normals.append([vertex, normal])
        if point_normals:
            self.apply_impulse(poly1, poly2, point_normals)
        return point_normals

    def notify(self, pairs):
        for pair in pairs:
            collidable1, collidable2 = pair
            if isinstance(collidable1.shape, Polygon) and isinstance(collidable2.shape, Polygon):
                self.find_minimum_push_vector(collidable1, collidable2)
                self.handle_poly_poly(collidable1, collidable2)
                pass


def check_vertex_edge(object1, object2):
    for i in range(object1.shape.order):
        v1 = object1.shape.get_transformed_vertices([object1.get_space()])[i]
        v2 = object1.shape.get_transformed_vertices([object1.get_space()])[(i + 1) % object1.shape.order]
        edge = v2 - v1
        u = edge.normalise()
        for v3 in object2.shape.get_transformed_vertices([object2.get_space()]):
            p = (v3 - v1)
            proj = u * (p * u)
            if abs(p ^ u) < 2 and 0 < p * p < edge * p:
                print("vertex-edge")
                return v3

    return 0


def do_narrow_phase(pairs):
    for pair in pairs:
        object1, object2 = pair
        if isinstance(object1.shape, Polygon) and isinstance(object2.shape, Polygon):

            for v1 in object1.shape.get_transformed_vertices([object1.get_space()]):
                for v2 in object2.shape.get_transformed_vertices([object2.get_space()]):
                    if abs(v1 - v2) < 2:
                        print("vertex-vertex")
                        return v1

            v = check_vertex_edge(object1, object2)
            if v:
                return v
            v = check_vertex_edge(object2, object1)
            if v:
                return v

            # check vertex-edge collisions
            # check intersection
            pass
