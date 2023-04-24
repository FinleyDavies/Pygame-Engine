from math import pi, sqrt
from vector import Vector, VectorSpace
from collisions import SweepPrune
import pygame
from pygame import gfxdraw

from random import randint

pygame.init()

# todo use numpy or opengl to transform the screen, 74% of the draw function is spent transforming
#  (transforming per point is inefficient)
# todo cache get_bounding_rect operation in broad phase collision detection
# todo use numpy to vectorise integration operations over all objects?


class Circle:
    def __init__(self, screen, radius, position, spaces=None, colour=None):
        if spaces is None:
            spaces = []
        self.theta = 0
        self.trail = []
        self.spaces = spaces
        self.screen = screen
        self.radius = radius
        self.mass = pi * radius ** 2
        self.position = position
        self.velocity = Vector()
        self.colour = (0, 0, 0) if colour is None else colour

    def draw(self):
        position = self.position.transform(self.spaces)
        pygame.gfxdraw.circle(self.screen, int(position[0]), int(position[1]), self.radius, self.colour)

    def update(self):
        self.trail.append(self.position)
        if len(self.trail) > 50:
            self.trail.pop(0)

        self.position += self.velocity / 60

        if self.position[0] - self.radius < 0:
            self.velocity.x = abs(self.velocity.x)
        if self.position[0] + self.radius > 400:
            self.velocity.x = -abs(self.velocity.x)
        if self.position[1] - self.radius < 0:
            self.velocity.y = abs(self.velocity.y)
        if self.position[1] + self.radius > 400:
            self.velocity.y = -abs(self.velocity.y)
        # self.velocity*=0.99

    def get_bounding_rect(self):
        minX = self.position[0] - self.radius
        minY = self.position[1] - self.radius
        maxX = self.position[0] + self.radius
        maxY = self.position[1] + self.radius
        return [minX, minY, maxX, maxY]

    def collide(self, other):
        pass
        # print("colliding")
        # position1 = self.position.convert(self.spaces)
        # position2 = other.position.convert(self.spaces)
        # pygame.draw.line(self.screen, (255,0,0), position1.getInt(),
        #                 position2.getInt(), 2)

    def draw_trail(self):
        for i in range(len(self.trail) - 2):
            pygame.draw.line(self.screen, (0, 0, 200), self.trail[i], self.trail[i + 1], 1)


def handle_collisions(sweep):
    broadPairs = sweep.get_broad_pairs()
    for pair in broadPairs:
        A, B = pair
        A.collide(B)

        if isinstance(A, Circle) and isinstance(B, Circle):
            normal = A.position - B.position
            relativeNormVel = normal / abs(normal) * (A.velocity - B.velocity)
            if abs(normal) < A.radius + B.radius and relativeNormVel < 1:
                # print("narrow")
                normal /= abs(normal)
                # print(relativeNormVel)
                numerator = (-2 * relativeNormVel)
                denominator = normal * normal * (A.mass + B.mass) / (A.mass * B.mass)
                impulse = numerator / denominator
                A.velocity += normal * impulse / A.mass
                B.velocity -= normal * impulse / B.mass


def main():
    from time import time

    pygame.init()
    pygame.font.init()
    font = pygame.font.SysFont(pygame.font.get_default_font(), 30)
    WIDTH, HEIGHT = 400, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    camera = VectorSpace()

    globalspace = VectorSpace((WIDTH, HEIGHT), pi)
    circles = []
    space2 = VectorSpace((30, 40), pi / 4)
    circles.append(Circle(screen, 10, Vector((200, 100)), [camera]))
    circles.append(Circle(screen, 10, Vector((250, 100)), [camera]))
    circles.append(Circle(screen, 10, Vector((300, 190)), [camera]))
    circles.append(Circle(screen, 10, Vector((500, 210)), [camera]))
    circles.append(Circle(screen, 10, Vector((400, 300)), [camera]))

    for i in range(100):
        circle = Circle(screen, 10, Vector((randint(20, WIDTH - 20), randint(20, HEIGHT - 20))), [camera])
        circle.velocity = Vector((randint(-100, 100), randint(-100, 100)))
        circles.append(circle)

    sp = SweepPrune(circles)

    clock = pygame.time.Clock()
    circles[0].velocity = Vector([2, 0])
    circles[1].velocity = Vector([1, 0])

    start  = time()
    fpss = []

    s = False
    running = True
    while running:

        if time() - start > 60:
            running = False
            break
        if len(fpss)+1 < time() - start:
            fpss.append(clock.get_fps())

        pygame.event.get()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mpos = pygame.mouse.get_pos()
                    circles.append(Circle(screen, 10, Vector(mpos), [camera]))
                    sp = SweepPrune(circles)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    camera.translate(Vector((-10, 0)))
                elif event.key == pygame.K_d:
                    camera.translate(Vector((10, 0)))

        for circle in circles:
            circle.draw()
            circle.update()
            circle.draw_trail()
        circles[0].draw_trail()
        circles[1].draw_trail()
        # print(circles[0].velocity)
        # print(circles[1].velocity)
        # circles[2].draw_trail()
        # circles[3].draw_trail()
        # circles[4].draw_trail()

        fps = clock.get_fps()
        # print(str(round(fps, 2)))
        text = font.render(str(round(fps, 1)), True, (0, 255, 0))
        # screen.blit(text, (50, 50))
        pygame.display.update()
        screen.fill((255, 255, 255))
        clock.tick()
        sp.update_values()
        handle_collisions(sp)
        # print(sp.overlapsX)

    print(f"avg fps: {sum(fpss)/len(fpss)}")


if __name__ == "__main__":
    main()
