import math
import pygame
from pygame.locals import *

CHARGES = [((0.5, 0.3), -1), ((0.3, 0.5), 1), ((0.7, 0.5), 1), ((0.5, 0.7), 1)]
RESOLUTION = 25
WINDOW_SIZE = 640
DIR_LEN = 16
MAX_SIZE = 50

pygame.init()

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

data = []
for i in range(RESOLUTION):
	row = []
	for j in range(RESOLUTION):
		row.append([0,0])
	data.append(row)

for (pos, charge) in CHARGES:
	for x in range(RESOLUTION):
		for y in range(RESOLUTION):

			reference_pos = (x/RESOLUTION, y/RESOLUTION)

			dist = math.hypot(pos[0] - reference_pos[0], pos[1] - reference_pos[1])

			if dist < 0.0001: continue;

			mag = charge / dist**2

			data[x][y][0] += mag * (reference_pos[0] - pos[0]) / dist
			data[x][y][1] += mag * (reference_pos[1] - pos[1]) / dist

mx = 0
for x in range(RESOLUTION):
	for y in range(RESOLUTION):
		mx = max(mx, math.hypot(data[x][y][0], data[x][y][1]))

sf = MAX_SIZE / mx

screen.fill((0,0,0))

for x in range(RESOLUTION):
	for y in range(RESOLUTION):
		mag = math.hypot(data[x][y][0], data[x][y][1])
		pygame.draw.line(screen, (255,255,0), (x/RESOLUTION*WINDOW_SIZE, y/RESOLUTION*WINDOW_SIZE), (x/RESOLUTION*WINDOW_SIZE + (DIR_LEN/mag)*data[x][y][0], y/RESOLUTION*WINDOW_SIZE + (DIR_LEN/mag)*data[x][y][1]))
		pygame.draw.line(screen, (255,255,255), (x/RESOLUTION*WINDOW_SIZE, y/RESOLUTION*WINDOW_SIZE), (x/RESOLUTION*WINDOW_SIZE + sf*data[x][y][0], y/RESOLUTION*WINDOW_SIZE + sf*data[x][y][1]))
		pygame.draw.circle(screen, (255,255,255), (int(x/RESOLUTION*WINDOW_SIZE), int(y/RESOLUTION*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/5), 1)

for (pos, charge) in CHARGES:
	for i in range(12):
		cur = [pos[0] + math.cos(i * math.pi / 6) * 0.02, pos[1] + math.sin(i*math.pi / 6) * 0.02]

		for i in range(50):
			tot = [0,0]

			for (pos1, charge1) in CHARGES:
				dist = math.hypot(pos1[0] - cur[0], pos1[1] - cur[1])

				if dist < 0.0001: continue;

				mag = charge1 / dist**2

				tot[0] += mag * (cur[0] - pos1[0]) / dist
				tot[1] += mag * (cur[1] - pos1[1]) / dist

			mag = math.hypot(tot[0], tot[1])

			if charge < 0:
				tot[0] *= -1
				tot[1] *= -1

			ncur = [cur[0] + tot[0] * 0.02 / mag, cur[1] + tot[1] * 0.02 / mag]
			#pygame.draw.line(screen, (255,255,255), (cur[0]*WINDOW_SIZE, cur[1]*WINDOW_SIZE), (ncur[0]*WINDOW_SIZE, ncur[1]*WINDOW_SIZE))
			cur = ncur[:]


for (pos, charge) in CHARGES:
	pygame.draw.circle(screen, (255,0,0) if charge > 0 else (0,0,255), (int(pos[0]*WINDOW_SIZE), int(pos[1]*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/3))

pygame.display.flip()

done = False
while not done:
	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			done = True