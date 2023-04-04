import pygame
from shapes import Collidable, Polygon, Circle
from constants import *
from vector import Vector
from collisions import SweepPrune, CollisionHandler
from random import randint as ran
import random
import time


class Graphics:
    def __init__(self, screen):
        self.screen = screen

    def draw_normals(self, normals):
        for normal in normals:
            p1 = normal[0].get_int()
            p2 = (normal[0] + normal[1] * 20).get_int()
            pygame.draw.line(self.screen, (255, 0, 255), p1, p2, 1)

    def draw_collidables(self, collidables):
        for collidable in collidables:
            if isinstance(collidable.shape, Circle):
                circle = collidable.shape
                pygame.draw.circle(self.screen, FOREGROUND_COLOUR, collidable.position, circle.radius, 1)

            elif isinstance(collidable.shape, Polygon):
                polygon = collidable.shape
                vertices = [vertex.transform([collidable.get_space()]) for vertex in polygon.get_vertices()]
                pygame.draw.polygon(self.screen, FOREGROUND_COLOUR, vertices, 1)
                pygame.draw.circle(self.screen, FOREGROUND_COLOUR,
                                   polygon.get_barycenter().transform([collidable.get_space()]).get_int(), 2)
                self.draw_vector(polygon.get_barycenter().transform([collidable.get_space()]),
                                 collidable.linear_velocity)

        ##            for vertex in [collidable.local_to_global(x) for x in polygon.vertices]:
        ##                vertex = collidable.global_to_local(vertex)
        ##                vel = collidable.get_point_velocity(vertex)
        ##                p1 = vertex.transform([collidable.get_space()]).get_int()
        ##                p2 = (vertex.transform([collidable.get_space()]) + vel*10).get_int()
        ##                pygame.draw.line(self.screen, (255, 0, 255), p1, p2, 1)
        # for tri in polygon.triangles:
        #   vertices = [vertex.transform([collidable.get_space()]) for vertex in tri.get_vertices()]
        #   pygame.draw.polygon(screen, FOREGROUND_COLOUR, vertices, 1)

        if DRAW_BOXES:
            for collidable in collidables:
                min_x, min_y, max_x, max_y = collidable.get_bounding_rect()
                pygame.draw.rect(self.screen, BOX_COLOUR, (min_x, min_y, max_x - min_x, max_y - min_y), 1)

    def draw_vector(self, position, direction):
        p1 = position.get_int()
        p2 = (position + direction * 10).get_int()
        pygame.draw.line(self.screen, (0, 255, 0), p1, p2, 2)

    def draw_object_normal(self, obj, point, detector):
        verts = obj.shape.get_transformed_vertices([obj.get_space()])
        for i in range(len(verts)):
            edge1 = verts[i]
            edge2 = verts[(i + 1) % len(verts)]
            normal = detector.check_vertex_edge(point, edge1, edge2)
            if normal is not None:
                self.draw_vector(point, normal)


def update_game_objects(collidables):
    for collidable in collidables:
        collidable.update_body()


def random_body(g):
    poly = Polygon([Vector((ran(-50, 50), ran(-50, 50))) for x in range(10)])
    # poly = Polygon([x*50 for x in [Vector((1,1)), Vector((1,-1)), Vector((-1,-1)), Vector((-1,1))]])
    poly.translate(-poly.get_barycenter())
    obj = Collidable(poly, 1, g)
    obj.position = Vector((ran(0, 800), ran(0, 800)))
    obj.orientation = 45
    # obj.linear_velocity = Vector((ran(-1,1),ran(-1,1)))
    # print(obj)
    return obj


def main():
    pygame.init()
    print("initialised")
    random.seed(1)

    screen = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))

    clock = pygame.time.Clock()

    shippoly = Polygon([x * 2 for x in [Vector((-30, 5)), Vector((-10, 10)), Vector((10, 10)), Vector((30, 5)),
                                        Vector((30, -5)), Vector((0, -15)), Vector((-30, -5))]])

    # floorpoly = Polygon([x*2 for x in [Vector((-200, 10)), Vector((200, 10)), Vector((200, -10)), Vector((-200, -10))]])
    shippoly.translate(-shippoly.get_barycenter())

    g = Graphics(screen)
    ship = Collidable(shippoly, 1, g)
    # ship.set_high_priority()

    ship.position = Vector((200, 200))
    ship.orientation = 180
    # ship.resolve_impulse(30000, Vector((0,0)), Vector((1, 1)).normalise())
    print("ship")
    # ship.orientation = 180
    # floor.angular_velocity = 1
    frames = 0

    objects = [ship]
    for i in range(1):
        print(i)
        objects.append(random_body(g))
    objects[1].resolve_impulse(50000, Vector((0, 0)), Vector((1, 1)).normalise())
    print("objects", len(objects))

    broad = SweepPrune(objects)
    narrow = CollisionHandler()
    print(broad, narrow)

    running = True
    t1 = time.time()
    while running:
        mousepos = Vector(pygame.mouse.get_pos())
        # ship.orientation += 5
        g.draw_collidables(objects)
        broad.update_values()
        pygame.display.update()
        update_game_objects(objects)
        v = narrow.notify(broad.get_broad_pairs())
        if v: g.draw_normals(v)

        ##        for o in objects:
        ##            g.draw_object_normal(o, mousepos, narrow)
        pygame.display.update()
        screen.fill(BACKGROUND_COLOUR)
        clock.tick(30)

        # ship.linear_velocity = Vector()
        # ship.position = Vector(pygame.mouse.get_pos())
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
        # if frames % 200 == 0:
        #    print(frames/(time.time() - t1))


if __name__ == "__main__":
    main()
