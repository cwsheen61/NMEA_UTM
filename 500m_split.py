import sys
import hashlib
import os
import struct

#format binary_little_endian 1.0


#ply
#format ascii 1.0
#comment UTM Zone 11S GPS Offsets X 505752.562929 Y 3615495.404042 Z 273.839000
#UTM Zone: 11S
#element vertex 257452676
#Point cloud points: 257452676
#property float x			0  f
#property float y			1  f
#property float z			2  f
#property float Nx			3  f
#property float Ny			4  f
#property float Nz			5  f
#property uchar red			6  i
#property uchar green			7  i
#property uchar blue			8  i
#property float intensity		9  f	
#property float point_range		10 f
#property double time			11 f
#comment initial pointcloud time:    1521610444.101754
#property float Easting			12 f
#property float Northing		13 f
#property int UTM_Zone_num		14 i
#property int UTM_ZONE_Alph		15 i
#property float Longitude		16 f
#property float Latitude		17 f
#property float trajectory_x		18 f
#property float trajectory_y		19 f
#property float trajectory_z		20 f
#property float trajectory_roll		21 f
#property float trajectory_pitch	22 f
#property float trajectory_yaw		23 f
#property float trajectory_time		24 f
#property float trajectory_Easting	25 f
#property float trajectory_Northing	26 f
#property int trajectory_UTM_Zone_num	27 i
#property int trajectory_UTM_ZONE_Alph	28 i
#property float trajectory_Longitude	29 f
#property float trajectory_Latitude	30 f
#end_header

def _Pack_pcLine(Line):
	packStr = '<3d3f3B5f2i11f2i2f'
	s = Line.split()
	x = float(s[0])
	y =  float(s[1])
	z = float(s[2])
	Nx = float(s[3])
	Ny = float(s[4])
	Nz = float(s[5])
	red = int(s[6])
	green = int(s[7])
	blue = int(s[8])
	inten = float(s[9])
	prange = float(s[10])
	time = float(s[11])
	e = float(s[12])
	n = float(s[13])
	UTMn = int(s[14])
	UTMa = int(s[15])
	lon = float(s[16])
	lat = float(s[17])
	tx = float(s[18])
	ty = float(s[19])
	tz = float(s[20])
	roll = float(s[21])
	pitch = float(s[22])
	yaw = float(s[23])
	ttime = float(s[24])
	te = float(s[25])
	tn = float(s[26])
	tUTMn = int(s[27])
	tUTMa = int(s[28])
	tlon = float(s[29])
	tlat = float(s[30])
	pack_data = struct.pack(packStr,x,y,z,Nx,Ny,Nz,red,green,blue,inten,prange,time,e,n,UTMn,UTMa,lon,lat,tx,ty,tz,roll,pitch,yaw,ttime,te,tn,tUTMn,tUTMa,tlon,tlat)
	return(pack_data)


pcFileName = raw_input('Input the name of the point cloud: ')
pcFileName = pcFileName.strip()
pcFileName = pcFileName.replace('\'','')
pcFileName = pcFileName.replace(' ','')

trFileName = pcFileName.replace('pointcloud','trajectory',1)

pc = open(pcFileName,'r')

pHeader = []
hasNormals = False
hasColor = False
while True:
	pcLine = pc.readline()
	if not pcLine: break
	
	sys.stdout.write(pcLine)
	sys.stdout.flush()
	pHeader.append(pcLine)
	if 'end_header' in pcLine: break

	if 'element' in pcLine:
		inStr = pcLine.split()
		pcPoints = long(inStr[2])


	if 'comment UTM' in pcLine:
		inStr = pcLine.split()
		UTM = inStr[3]

		sys.stdout.write('UTM Zone: %s\n' % UTM)
		sys.stdout.flush()
	if 'Nx' in pcLine:
		hasNormals = True

	if 'green' in pcLine:
		hasColor = True
	if 'GREEN' in pcLine:
		hasColor = True
	if 'G ' in pcLine:
		hasColor = True
	if 'GRN' in pcLine:
		hasColor = True
	if 'grn' in pcLine:
		hasColor = True

sys.stdout.write('Point cloud points: %d\n' % pcPoints)
sys.stdout.flush()

xMax = yMax = 0.0
xMin = yMin = 10000000.0	

index = 0

while True:
	pcLine = pc.readline()
	if not pcLine: break
	inStr = pcLine.split()
	x = float(inStr[0])
	y = float(inStr[1])
	if x > xMax: xMax = x
	if x < xMin: xMin = x
	if y > yMax: yMax = y
	if y < yMin: yMin = y
	
	if float(index/100000) == float(index)/100000.0:
		sys.stdout.write('\rIndex: %d %f %f %f %f %f %f' % (index, xMin, xMax, (xMax - xMin), yMin, yMax, (yMax - yMin)))
		sys.stdout.flush()
	index += 1
#	if index == 20000000: break

pc.close()
	
xRange = xMax - xMin
yRange = yMax - yMin

xGrids = int(xRange/500)+2
yGrids = int(yRange/500)+2

totalGrids = (xGrids * yGrids)

print ('\n %d %d %d' % (xGrids, yGrids, totalGrids))

xGridMin = int(500 * int(xMin/500))
xGridMax = int(500 * int(xMax/500))
yGridMin = int(500 * int(yMin/500))
yGridMax = int(500 * int(yMax/500))

print ('Grid Corners (%d, %d) to (%d, %d)' % (xGridMin, yGridMin, xGridMax, yGridMax))

f = [[0 for i in range(yGrids+2)]for j in range(xGrids+2)]

for i in range (xGrids):
	for j in range(yGrids):
		xName = xGridMin + int(500*i)
		yName = yGridMin + int(500*j)
		fileNameStr = ('/home/realearth/recordings/%s_%dE_%dN.tmp' % (UTM, xName, yName))
#		print 'i: ', i, 'j: ', j
		f[i][j] = open(fileNameStr,'wb')

pc = open(pcFileName,'r')

while True:
	pcLine = pc.readline()
	if 'end_header' in pcLine: break

index = 0
while True:
	pcLine = pc.readline()
	if not pcLine: break
	index += 1
	if float(index/100000) == float(index)/100000.0:
		sys.stdout.write('\rWriting %s temp file, Index: %d' % (fileNameStr,index))
		sys.stdout.flush()
#	if index == 20000000: break
	inStr = pcLine.split()
	x = float(inStr[0])
	y = float(inStr[1])

	xBin = int((x - xMin)/500)
	yBin = int((y - yMin)/500)
	outputStr = ''
	for l in range(len(inStr)):
		outputStr += (inStr[l] + ' ')
		if l == 2:
			if not hasNormals:
				outputStr += '0.0 0.0 0.0 '
			if not hasColor:
				outputStr += '255 255 255 '
	pack_data = _Pack_pcLine(outputStr)
	f[xBin][yBin].write(pack_data)


for i in range (xGrids):
	for j in range(yGrids):
		f[i][j].close()

sys.stdout.write('\n')
sys.stdout.flush()

struct_fmt = '<3d3f3B5f2i11f2i2f'
struct_len = struct.calcsize(struct_fmt)
struct_unpack = struct.Struct(struct_fmt).unpack_from


for i in range (xGrids):
	for j in range(yGrids):
		xName = xGridMin + int(500*i)
		yName = yGridMin + int(500*j)
		fileNameStr = ('/home/realearth/recordings/%s_%dE_%dN.tmp' % (UTM, xName, yName))
		f[i][j] = open(fileNameStr,'rb')
		index = 0
		hsh = hashlib.sha512()
		sys.stdout.write('\rHashing: %s' % fileNameStr)
		sys.stdout.flush()
		while True:
			pack_data = f[i][j].read(struct_len)
			if not pack_data: break
#			pack_data = _Pack_pcLine(pcLine)
			hsh.update(pack_data)
			index += 1
		f[i][j].close
		sys.stdout.write('\nSHA512: %s\n' % hsh.hexdigest())
		sys.stdout.flush()
		if index > 0:
			outFileName = fileNameStr.replace('tmp','ply',1)
			out = open(outFileName,'wb')
			for k in range (len(pHeader)):
				if 'element' in pHeader[k]:
					out.write('element vertex %d\n' % index)
				elif 'format' in pHeader[k]:
					out.write('format binary_little_endian 1.0\n')
				elif 'double time' in pHeader[k]:
					out.write('property float time\n')
				elif 'property float x' in pHeader[k]:
					out.write('property double x\n')
				elif 'property float y' in pHeader[k]:
					out.write('property double y\n')
				elif 'property float z' in pHeader[k]:
					out.write('property double z\n')
					if not hasNormals:
						out.write('property float Nx\n')
 						out.write('property float Ny\n')
						out.write('property float Nz\n')
					if not hasColor:
						out.write('property uchar red\n')
						out.write('property uchar green\n')
						out.write('property uchar blue\n')
				elif 'end_header' in pHeader[k]:
					out.write('comment SHA512: %s\n' % hsh.hexdigest())
					out.write(pHeader[k])
				else: out.write(pHeader[k])
#			exit ()
			f[i][j] = open(fileNameStr,'rb')
			pIndex = 0
			sys.stdout.write('\n')
			while True:
				pack_data = f[i][j].read(struct_len)
				if not pack_data: break
				pIndex += 1
				if float(pIndex/100000) == float(pIndex)/100000.0:
					sys.stdout.write('\rIndex: %d' % pIndex)
					sys.stdout.flush()
				out.write(pack_data)
		f[i][j].close()
		os.remove(fileNameStr)

sys.stdout.write('\n')
sys.stdout.flush()

		
		

