import math
import pygame
from pygame.locals import *



#Problem specification
POINT_CHARGES = [((0.3, 0.3), -0.1), ((0.35, 0.35), 0.1)]
CHARGE_PLATES = [((0.8, 0.2), (0.8, 0.8), 1), ((0.2, 0.2), (0.2, 0.8), -1)]

#Display
WINDOW_SIZE = 640
#Grid plot
SHOW_GRID = False
RESOLUTION = 25
DIR_LEN = 16
MAX_SIZE = 50
#Field line plot
SHOW_FIELD_LINES = True
SHOW_EQUIPOTENTIAL_LINES = False
EQUIPOTENTIAL_STEPS = 50
MAX_EQUI_DIST = 0.1
USE_RUNGE_KUTTA = True
DELTA = 0.0005
STEPS = 9000
POINT_COUNT = 20
PLATE_DENSITY = 120

done = False



#Normalize a vector
def norm(v):
	mag = math.hypot(v[0], v[1])
	return [v[0] / mag, v[1] / mag]

#Sum the fields for all point charges & plates at this point
def fieldPoint(x, y):
	tot = [0,0]
	for (pos, charge) in POINT_CHARGES:
		dist = math.hypot(pos[0] - x, pos[1] - y)

		if dist < 0.0001: continue;

		mag = charge / dist**2

		tot[0] += mag * (x - pos[0]) / dist
		tot[1] += mag * (y - pos[1]) / dist

	for (start, end, charge) in CHARGE_PLATES:
		#Plate length
		L = math.hypot(start[0] - end[0], start[1] - end[1])

		plate_dir = norm([end[0] - start[0], end[1] - start[1]])
		point_dir = [x - start[0], y - start[1]]

		if math.hypot(point_dir[0], point_dir[1]) < 0.0001: continue;

		#Horizontal distance along plate
		a = plate_dir[0] * point_dir[0] + plate_dir[1] * point_dir[1]

		#Perpendicular distance from plate
		b = point_dir[0] * plate_dir[1] - point_dir[1] * plate_dir[0]

		#Derived from: http://online.cctt.org/physicslab/content/phyapc/lessonnotes/Efields/EchargedRods.asp
		try:
			additional = [0,0]
			additional[0] = charge * (-1/((L-a)**2 + b**2)**0.5 + 1/(a**2 + b**2)**0.5)
			additional[1] = charge * math.copysign(((L-a)/((L-a)**2 + b**2)**0.5 + a/(a**2 + b**2)**0.5)/b**2, b)

			tot[0] += plate_dir[0] * additional[0] + plate_dir[1] * additional[1]
			tot[1] -= plate_dir[1] * additional[0] + plate_dir[0] * additional[1]
		except:
			pass

	return tot

#Fourth order runge kutta
def rungeKutta(x, y, f, delta):

	k1 = norm(f(x,y))
	k2 = norm(f(x + k1[0] * delta / 2, y + k1[0] * delta / 2))
	k3 = norm(f(x + k2[0] * delta / 2, y + k2[0] * delta / 2))
	k4 = norm(f(x + k3[0] * delta, y + k3[0] * delta))

	return [x + (k1[0] + 2*k2[0] + 2*k3[0] + k4[0]) * delta / 6, y + (k1[1] + 2*k2[1] + 2*k3[1] + k4[1]) * delta / 6]

#Traces a field line & updates array to construct equipotential lines
def fieldLine(cur, charge, equipotential_points):
	pd = 0
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

		#Use average field to calculate delta V
		if SHOW_EQUIPOTENTIAL_LINES:
			p0 = fieldPoint(cur[0], cur[1])
			p1 = fieldPoint(ncur[0], ncur[1])

			mag = (math.hypot(p0[0], p0[1]) + math.hypot(p1[0], p1[1])) / 2
			pd += mag * DELTA

			try:
				step = int(pd / EQUIPOTENTIAL_STEPS)
				if equipotential_points[step][i] == None:
					equipotential_points[step][i] = ncur
			except:
				while len(equipotential_points) <= step:
					equipotential_points.append([None] * LINE_COUNT)

		if SHOW_FIELD_LINES:
			pygame.draw.line(screen, (255,255,255), (cur[0]*WINDOW_SIZE, cur[1]*WINDOW_SIZE), (ncur[0]*WINDOW_SIZE, ncur[1]*WINDOW_SIZE))

		#Refresh screen
		if not j % 200:
			draw()

		#Terminate if field line leaves screen or reaches charge
		if not (0 < ncur[0] < 1 and 0 < ncur[1] < 1): break;
		terminate = False
		for (pos1, charge1) in POINT_CHARGES:
			if math.hypot(ncur[0] - pos1[0], ncur[1] - pos1[1]) < 1 / RESOLUTION / 3:
				terminate = True
				break;
		for (start, end, charge1) in CHARGE_PLATES:
			point_dir = [ncur[0] - start[0], ncur[1] - start[1]]
			plate_dir = norm([end[0] - start[0], end[1] - start[1]])
			if abs(point_dir[0] * plate_dir[1] - point_dir[1] * plate_dir[0]) < 1 / RESOLUTION / 9:
				terminate = True
				break;
		if terminate: break;

		cur = ncur[:]

		j += 1

#Draws all equipotential lines for the data
def drawEquipotential(equipotential_points):
	#Linearly interpolate for missing points
	for i in range(POINT_COUNT):
		last_idx = -1
		last = None

		for j in range(len(equipotential_points)):
			if equipotential_points[j][i] != None:
				#Data missing
				if last_idx != j - 1:
					for k in range(last_idx + 1, j):
						if last == None:
							equipotential_points[k][i] = equipotential_points[j][i]
						else:
							equipotential_points[k][i] = [0,0]
							equipotential_points[k][i][0] = equipotential_points[j][i][0] * (k - last_idx) / (j - last_idx) + equipotential_points[last_idx][i][0] * (j - k) / (j - last_idx)
							equipotential_points[k][i][1] = equipotential_points[j][i][1] * (k - last_idx) / (j - last_idx) + equipotential_points[last_idx][i][1] * (j - k) / (j - last_idx)

				last_idx = j
				last = equipotential_points[j][i]

	#Draw line segments if they are short enough
	cnt = len(equipotential_points)
	for line in equipotential_points:
		for i in range(cnt):
			if line[i] == None or line[(i+1) % cnt] == None: continue;
			if math.hypot(line[i][0] - line[(i+1) % cnt][0], line[i][1] - line[(i+1) % cnt][1]) > MAX_EQUI_DIST: continue;
			pygame.draw.line(equipotential_surface, (255,0,0, 255),
				(line[i][0]*WINDOW_SIZE, line[i][1]*WINDOW_SIZE),
				(line[(i+1) % cnt][0]*WINDOW_SIZE, line[(i+1) % cnt][1]*WINDOW_SIZE),
				2)

#Clear event queue & flip buffers
def draw():
	global done

	pygame.display.flip()
	for ev in pygame.event.get():
		if ev.type == pygame.QUIT:
			done = True


pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
screen.fill((0,0,0))
equipotential_surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
equipotential_surface.fill((0,0,0,0))

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

if SHOW_FIELD_LINES or SHOW_EQUIPOTENTIAL_LINES:
	#Contructs field lines numerically
	for (pos, charge) in POINT_CHARGES:

		equipotential_points = []

		for i in range(POINT_COUNT):
			theta = 2 * i * math.pi / POINT_COUNT
			cur = [pos[0] + math.cos(theta) / RESOLUTION / 3, pos[1] + math.sin(theta) / RESOLUTION / 3]

			fieldLine(cur, charge, equipotential_points)

		if SHOW_EQUIPOTENTIAL_LINES and charge > 0:
			drawEquipotential(equipotential_points)

	for (start, end, charge) in CHARGE_PLATES:

		equipotential_points = []

		cnt = int(PLATE_DENSITY * math.hypot(end[0] - start[0], end[1] - start[1]))
		for i in range(cnt):
			pos = 2 * abs(i - cnt / 2) / cnt
			cur = [start[0] + pos * (end[0] - start[0]), start[1] + pos * (end[1] - start[1])]

			delta = norm([end[0] - start[0], end[1] - start[1]])

			if i > cnt / 2:
				cur = [cur[0] + delta[1] / RESOLUTION / 6, cur[1] - delta[0] / RESOLUTION / 6]
			else:
				cur = [cur[0] - delta[1] / RESOLUTION / 6, cur[1] - delta[0] / RESOLUTION / 6]

			fieldLine(cur, charge, equipotential_points)

		if SHOW_EQUIPOTENTIAL_LINES and charge > 0:
			drawEquipotential(equipotential_points)

					
#Display the charges
for (pos, charge) in POINT_CHARGES:
	pygame.draw.circle(screen, (255,0,0) if charge > 0 else (0,0,255), (int(pos[0]*WINDOW_SIZE), int(pos[1]*WINDOW_SIZE)), int(WINDOW_SIZE/RESOLUTION/3))
for (start, end, charge) in CHARGE_PLATES:
	pygame.draw.line(screen, (255,0,0) if charge > 0 else (0,0,255),
		(int(start[0]*WINDOW_SIZE), int(start[1]*WINDOW_SIZE)),
		(int(end[0]*WINDOW_SIZE), int(end[1]*WINDOW_SIZE)),
		 int(WINDOW_SIZE/RESOLUTION/6))

screen.blit(equipotential_surface, (0,0))

while not done:
	draw()