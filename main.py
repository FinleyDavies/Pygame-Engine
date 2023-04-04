import pygame
from vector import Vector, VectorSpace
from math import sin, cos, pi
from random import randint as ran




class Hovercraft:
	# velocity at point P in local space;
	# self.localVelocity + P ^ self.angularVelocity
	def __init__(self):
		self.mass = 100
		self.inertia = 40000

		self.position = Vector((400, 400))
		self.orientation = 0		# defined in radians

		self.space = VectorSpace()
		self.polygon = [Vector((-30, 5)), Vector((-10, 10)), Vector((10,10)), Vector((30, 5)), Vector((30, -5)), Vector((0,-15)), Vector((-30, -5))]

		self.localVelocity = Vector()
		self.speed = abs(self.localVelocity)
		self.globalVelocity = Vector()
		self.angularVelocity = 0

		self.resultantForce = Vector()
		self.moment = 0

		self.thrusters = {}


	def calcThrust(self):
		self.resultantForce = Vector()
		self.moment = 0

		#V^(V*s) = s(V^V)
		#print(self.thrusters)
		for values in self.thrusters.values():
			#print(values)
			position, force, enabled = values
			if enabled:
				self.resultantForce += force
				self.moment += position ^ force
				#print(self.moment)

		self.resultantForce.rotate_ip(self.orientation)

	def updateBodyEuler(self, dt):
		self.calcThrust()
		a = self.resultantForce / self.mass + Vector((0,0.01))
		dv = a * dt
		self.globalVelocity += dv
		ds = self.globalVelocity * dt
		self.position += ds

		aa = self.moment / self.inertia
		dav = aa * dt
		self.angularVelocity += dav
		das = self.angularVelocity * dt
		self.orientation += das

		self.space.position = self.position
		self.space.direction = self.orientation
		self.localVelocity = self.globalVelocity.rotate(-self.orientation)

	def addThruster(self, key, position, force):
		self.thrusters[key] = [Vector(position), Vector(force), False]

	def setThrusters(self, keys):
		for key in self.thrusters:
			self.thrusters[key][2] = keys[key]

	def modulateThrust(self):
		pass

class Camera:
	def __init__(self):
		self.space = VectorSpace((400,400))
		self.originalSpace = self.space
		self.shaking = False
		self.T = 0

	def track(self, position, tolerance=100):
		v = Vector(position)-self.space.position
		if abs(v) > tolerance:
			displacement = v/abs(v) * (abs(v)-tolerance)/2
			self.space.position += displacement
		#print(position, self.space.position)

	def start_shake(self):
		self.shaking = True
		self.originalSpace = self.space

	def shake(self, dt):
		def noise(t):
			t=2*pi*t/20
			x = cos(20 * pi * t) - sin(14 * pi * t)
			y = sin(2 * pi * t) - cos(24 * pi * t)
			return Vector((x, y))*5

		def noise2():
			x = ran(-10,10)
			y = ran(-10,10)
			return Vector((x,y))

		if self.shaking:
			self.T += dt
			v = noise(self.T)
			space = self.originalSpace
			space.translate(v)
			self.space= space
			if self.T > 20:
				self.space = self.originalSpace
				self.shaking = False
				self.T = 0





		#\left(\cos2\pi t-\sin14\pi t,\sin2\pi t-1\cos24\pi t\right)
		#\left(\cos2\pi t-\sin14\pi t,\sin2\pi t-1\cos24\pi t\right)



def draw(craft, camera, screen):
	# Having actors draw themselves is not a good design
	verts = [v.convert([craft.space, -camera.space,VectorSpace((400,400))]).toPoint() for v in craft.polygon]
	verts2 = [v.convert([VectorSpace((700, 100), craft.orientation)]).toPoint() for v in craft.polygon]
	pygame.draw.polygon(screen, (255, 255, 255), verts, 2)
	pygame.draw.polygon(screen, (255, 255, 255), verts2, 2)
	#pygame.draw.circle(screen, (255,150,150), (400,400), 100, 2)

	for i in range(100):
		p = Vector((i*100, i*100))
		p = p.convert([-camera.space, VectorSpace((400,400))]).toPoint()
		pygame.draw.circle(screen, (255,255,255), p, 30)

def main():
	pygame.init()
	WIDTH, HEIGHT = 800, 800
	BGCOLOUR = (0, 0, 0)
	screen = pygame.display.set_mode((WIDTH, HEIGHT))

	clock = pygame.time.Clock()
	craft = Hovercraft()
	craft.addThruster(pygame.K_a, Vector((-30, 0)), Vector((0, -1)))
	craft.addThruster(pygame.K_d, Vector((30, 0)), Vector((0, -1)))

	print(craft.thrusters)

	camera = Camera()



	running = True
	while running:
		craft.setThrusters(pygame.key.get_pressed())
		if pygame.key.get_pressed()[pygame.K_w]:
			camera.start_shake()
		craft.updateBodyEuler(1)
		camera.track(craft.position)
		camera.shake(0.1)
		draw(craft, camera, screen)
		pygame.display.update()
		screen.fill(BGCOLOUR)
		clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
				pygame.quit()


if __name__ == "__main__":
	main()
	exit()
