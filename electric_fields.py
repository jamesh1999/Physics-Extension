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



pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
screen.fill((0,0,0))

if SHOW_GRID:
	#Initialise grid array & populate
	data = []
	for x in range(RESOLUTION):
		row = []
		for x in range(RESOLUTION):
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
	#Contructs field lines by the Euler method
	for (pos, charge) in CHARGES:
		for i in range(12):
			cur = [pos[0] + math.cos(i * math.pi / 6) * 0.02, pos[1] + math.sin(i*math.pi / 6) * 0.02]

			for i in range(50):
				tot = fieldPoint(cur[0], cur[1])
				mag = math.hypot(tot[0], tot[1])

				if charge < 0:
					tot[0] *= -1
					tot[1] *= -1

				ncur = [cur[0] + tot[0] * 0.02 / mag, cur[1] + tot[1] * 0.02 / mag]
				pygame.draw.line(screen, (255,255,255), (cur[0]*WINDOW_SIZE, cur[1]*WINDOW_SIZE), (ncur[0]*WINDOW_SIZE, ncur[1]*WINDOW_SIZE))
				cur = ncur[:]


#Display the charges
for (pos, charge) in CHARGES:
	pygame.draw.circle(screen, (255,0,0) if charge > 0 else (0,0,255), (int(pos[0]*WINDOW_SIZE), int(pos[1]*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/3))

pygame.display.flip()

done = False
while not done:
	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			done = True