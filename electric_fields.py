import math
import pygame
from pygame.locals import *



#Problem specification
CHARGES = [((0.5, 0.3), -1), ((0.3, 0.5), 1), ((0.7, 0.5), 1), ((0.5, 0.7), 1)]

#Display
WINDOW_SIZE = 640
#Grid plot
SHOW_GRID = False
RESOLUTION = 25
DIR_LEN = 16
MAX_SIZE = 50
#Field line plot
SHOW_FIELD_LINES = True
USE_RUNGE_KUTTA = True
DELTA = 0.0001
STEPS = 0
LINE_COUNT = 12



#Sum the fields for all point charges at this point
def fieldPoint(x, y):
	tot = [0,0]
	for (pos, charge) in CHARGES:
		dist = math.hypot(pos[0] - x, pos[1] - y)

		if dist < 0.0001: continue;

		mag = charge / dist**2

		tot[0] += mag * (x - pos[0]) / dist
		tot[1] += mag * (y - pos[1]) / dist

	return tot

#Fourth order runge kutta
def rungeKutta(x, y, f, delta):

	def norm(v):
		mag = math.hypot(v[0], v[1])
		return [v[0] / mag, v[1] / mag]

	k1 = norm(f(x,y))
	k2 = norm(f(x + k1[0] * delta / 2, y + k1[0] * delta / 2))
	k3 = norm(f(x + k2[0] * delta / 2, y + k2[0] * delta / 2))
	k4 = norm(f(x + k3[0] * delta, y + k3[0] * delta))

	return [x + (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * delta / 6, y + (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * delta / 6]



pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
screen.fill((0,0,0))

if SHOW_GRID:
	#Initialise grid array & populate
	data = []
	for x in range(RESOLUTION):
		row = []
		for y in range(RESOLUTION):
			row.append(fieldPoint(x/RESOLUTION, y/RESOLUTION))
		data.append(row)

	#Normalize line length by largest magnitude
	mx = 0
	for x in range(RESOLUTION):
		for y in range(RESOLUTION):
			mx = max(mx, math.hypot(data[x][y][0], data[x][y][1]))
	sf = MAX_SIZE / mx

	#Display
	for x in range(RESOLUTION):
		for y in range(RESOLUTION):
			mag = math.hypot(data[x][y][0], data[x][y][1])
			#Direction vector
			pygame.draw.line(screen, (255,255,0),
				(x/RESOLUTION*WINDOW_SIZE, y/RESOLUTION*WINDOW_SIZE),
				(x/RESOLUTION*WINDOW_SIZE + (DIR_LEN/mag)*data[x][y][0], y/RESOLUTION*WINDOW_SIZE + (DIR_LEN/mag)*data[x][y][1]))
			#Magnitude vector
			pygame.draw.line(screen, (255,255,255),
				(x/RESOLUTION*WINDOW_SIZE, y/RESOLUTION*WINDOW_SIZE),
				(x/RESOLUTION*WINDOW_SIZE + sf*data[x][y][0], y/RESOLUTION*WINDOW_SIZE + sf*data[x][y][1]))
			#Compass ring
			pygame.draw.circle(screen, (255,255,255), (int(x/RESOLUTION*WINDOW_SIZE), int(y/RESOLUTION*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/5), 1)

if SHOW_FIELD_LINES:
	#Contructs field lines numerically
	for (pos, charge) in CHARGES:
		for i in range(LINE_COUNT):
			theta = 2 * i * math.pi / LINE_COUNT
			cur = [pos[0] + math.cos(theta) / RESOLUTION / 3, pos[1] + math.sin(theta) / RESOLUTION / 3]

			j = 0
			while STEPS == 0 or j < STEPS:

				def negPoint(x, y):
					val = fieldPoint(x, y)
					return [-val[0], -val[1]]

				if USE_RUNGE_KUTTA:
					ncur = rungeKutta(cur[0], cur[1], fieldPoint if charge > 0 else negPoint, DELTA)
				else:
					#Otherwise perform the Euler method
					tot = fieldPoint(cur[0], cur[1])
					mag = math.hypot(tot[0], tot[1])

					if charge < 0:
						tot[0] *= -1
						tot[1] *= -1

					ncur = [cur[0] + tot[0] * DELTA / mag, cur[1] + tot[1] * DELTA / mag]

				pygame.draw.line(screen, (255,255,255), (cur[0]*WINDOW_SIZE, cur[1]*WINDOW_SIZE), (ncur[0]*WINDOW_SIZE, ncur[1]*WINDOW_SIZE))

				#Refresh screen
				if not j % 200:
					pygame.display.flip()

				#Terminate if field line leaves screen or reaches charge
				if not (0 < ncur[0] < 1 and 0 < ncur[1] < 1): break;
				terminate = False
				for (pos1, charge1) in CHARGES:
					if math.hypot(ncur[0] - pos1[0], ncur[1] - pos1[1]) < 1 / RESOLUTION / 3:
						terminate = True
						break;
				if terminate: break;

				cur = ncur[:]

				j += 1


#Display the charges
for (pos, charge) in CHARGES:
	pygame.draw.circle(screen, (255,0,0) if charge > 0 else (0,0,255), (int(pos[0]*WINDOW_SIZE), int(pos[1]*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/3))

pygame.display.flip()

done = False
while not done:
	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			done = True