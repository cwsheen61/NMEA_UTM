import sys
from math import sqrt

grid = 20

header = []
x = []
y = []
z = []
gx = []
gy = []
gz = []
t = []


gpsFileName = input ('Input GPS File Name: ')
skip = input ('Input number of points to skip: ')

g = open(gpsFileName,'r')
headLine = 0

for line in g:
	header.append(line)
	headLine += 1
	if line == 'end_header\n':
		break
for i in range (headLine):
	splitStr = header[i].split(' ')
	if splitStr[0] == 'element':
		if splitStr[1] == 'vertex':
			numVertex = int(splitStr[2])
			newVertex = numVertex/skip + 1
			header[i]=('element vertex %d\n' % newVertex)
 
numPts = 0
for line in g:
	inStr = line.split(' ')
	x.append(float(inStr[0]))
	y.append(float(inStr[1]))
	z.append(float(inStr[2]))
	gx.append(float(inStr[3]))
	gy.append(float(inStr[4]))
	gz.append(float(inStr[5]))
	t.append(float(inStr[6]))
	numPts += 1	

count = 0
sumAlt = 0.0


for j in range(numPts):
	for k in range(numPts):
		if sqrt((gx[j] -gx[k])**2 + (gy[j]-gy[k])**2) <= grid:
			sumAlt += gz[k]
			count +=1
	gz[j] = sumAlt / float(count)
	count = 0
	sumAlt = 0.0

g.close()

outFileName = gpsFileName.replace('GPS','GPS_out',1)

g = open(outFileName,'w')

for i in range(headLine):
	g.write('%s' % header[i])

for i in range(numPts):
	if float(i/skip)==float(i)/float(skip):
		g.write('%f %f %f %f %f %f %f\n' % (x[i], y[i], z[i], gx[i], gy[i], gz[i], t[i]))

g.close()
