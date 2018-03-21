#!/usr/bin/env python

# 	create_gps_ply.py
#	version 0.6
#	1 December 2017
#	Changed search algorithm to successively narrow the search ranges from 200s centered
#	around the starting time down to 0.1s steps
# 	
#	changed the files to search on entire trajectory first, then reduce by the skipnum
#	eliminate the offset guess value, as it is no longer needed
#	set to compare "speed" and added zero trap
#


import sys
import os

gpsArray = [[0.0 for i in range(5)] for j in range(1)]
trajArray = [[0.0 for i in range(7)] for j in range (12)]
plyArray = [[0.0 for i in range(7)] for j in range(13)]

gpsInFileName = sys.argv[1]
trajInFileName = sys.argv[2]
skipNum = sys.argv[3]
nowTime = sys.argv[4]

print 'create_gps_ply.py version 0.5, pre-release, 1 December 2017'
print 'written by C. Wade Sheen, Kaarta'
print 'copyright 2017 by Kaarta'


pathName, tail = os.path.split(trajInFileName)

slash = "/"

pathName = '%s%s' % (pathName, slash)

gpsInFileName = '%s%s' % (pathName, gpsInFileName)
gpsLineCount = 0
gpsInArray = []
with open(gpsInFileName, 'r') as gpsInFile:
	headerLine = gpsInFile.readline
	for line in gpsInFile:
		gpsInArray.append(line)
		gpsLineCount += 1
		
gpsInFile.close()

trajLineCount = 0
trajInArray = []
with open(trajInFileName,'r') as trajInFile:
	for line in trajInFile:
		trajInArray.append(line)
		trajLineCount += 1

trajInFile.close()

print ("GPS lines: %d" % gpsLineCount)
print ("Trajectory lines %d" % trajLineCount)


for i in range(1,gpsLineCount):
	s_gpsX, s_gpsY, s_gpsZ, s_Zcorrect, s_HDOP, s_gpsTime, sUTM = gpsInArray[i].split(' ',7)
	gpsArray.append([0,0,0,0,0])
	gpsArray[i][0] = float(s_gpsX)
	gpsArray[i][1] = float(s_gpsY)
	gpsArray[i][2] = float(s_gpsZ)
	gpsArray[i][3] = float(s_gpsTime)
	if i == 1:
		initUTM = sUTM
	
# for AgJunction only
#
#sum = 0.0
#
#for i in range(1,gpsLineCount):
#	sum += gpsArray[i][2]
#
#averageZ = sum/float(gpsLineCount)
#
#for i in range(1, gpsLineCount):
#	gpsArray[i][2] = averageZ
#	
	
 	time = gpsArray[i][3]
 	
	gpsArray[i][3] = time
	if i > 1:
		if gpsArray[i][3] <> gpsArray[i-1][3]:
			gpsArray[i][4] = (((gpsArray[i][0] - gpsArray[i-1][0])**2 + (gpsArray[i][1] - gpsArray[i-1][1])**2 + (gpsArray[i][2] - gpsArray[i-1][2])**2)**(1.0/2.0))/(gpsArray[i][3] - gpsArray[i-1][3])
		else: gpsArray[i][4] = 0

for i in range(11, trajLineCount):
	s_trajX, s_trajY, s_trajZ, s_trajR, s_trajP, s_trajYaw, s_trajTime = trajInArray[i].split(' ',7)
	trajArray.append([0,0,0,0,0,0,0])
	trajArray[i][0] = float(s_trajX)
	trajArray[i][1] = float(s_trajY)
	trajArray[i][2] = float(s_trajZ)
	trajArray[i][3] = float(s_trajTime)
	if i > 1:
		if trajArray[i][3] <> trajArray[i-1][3]:
			trajArray[i][4] = (((trajArray[i][0] - trajArray[i-1][0])**2 + (trajArray[i][1] - trajArray[i-1][1])**2 + (trajArray[i][2] - trajArray[i-1][2])**2)**(1.0/2.0))/(trajArray[i][3] - trajArray[i-1][3])
		else: trajArray[i][4] = 0
	
timeOffsetGuess = trajArray[trajLineCount-1][3] - gpsArray[gpsLineCount-1][3]
print 'Offset appears to be around: ', timeOffsetGuess, ' seconds.'

sweepStep = 102.4

while sweepStep >= 0.1:
#	print 'sweepStep: ', sweepStep
	sweepStart = -(10.0 * sweepStep) + timeOffsetGuess
	sweepEnd = (10.0 * sweepStep) + timeOffsetGuess
	maxSumProduct = 0.0
	offsetTime = 0.0

	sweep = sweepStart
	k = 0
	while sweep <= sweepEnd:
		sumProduct = 0
		arrayIndex = 11
		for i in range(1, gpsLineCount):
			searchTime = gpsArray[i][3] + sweep
			sys.stdout.write('\r sweepStep: %f Search time: %f maxSumProduct: %f at: %f' % (sweepStep, sweep, maxSumProduct, offsetTime))
			sys.stdout.flush()
			found = 0	
			arrayIndex = 11
			while found <> 1:
				if trajArray[arrayIndex][3] >= searchTime:
					found = 1
					sumProduct = sumProduct + (gpsArray[i][4] * trajArray[arrayIndex][4])
					arrayIndex += 1
				else: 
					arrayIndex += 1
				if arrayIndex == trajLineCount-1:
					found = 1
		if sumProduct > maxSumProduct:
			maxSumProduct = sumProduct
			offsetTime =sweep
#			print ("Maximum sum of products: %6.0f \nAt offset time: %6.2f " % (maxSumProduct, offsetTime))

		sweep += sweepStep
	timeOffsetGuess = offsetTime
	sweepStep = sweepStep / 4.0
	print ("\nMaximum sum of products: %6.0f \nAt offset time: %6.2f " % (maxSumProduct, offsetTime))

plyIndex = 12
for i in range (1, gpsLineCount):
	searchTime = gpsArray[i][3] + offsetTime
	found = 0
	arrayIndex = 11
	while found <> 1:
		if trajArray[arrayIndex][3] >= searchTime:
			found = 1
			plyArray[plyIndex][0] = trajArray[arrayIndex][0]
			plyArray[plyIndex][1] = trajArray[arrayIndex][1]
			plyArray[plyIndex][2] = trajArray[arrayIndex][2]
			plyArray[plyIndex][3] = gpsArray[i][0] - gpsArray[1][0]
			plyArray[plyIndex][4] = gpsArray[i][1] - gpsArray[1][1]
			plyArray[plyIndex][5] = gpsArray[i][2] - gpsArray[1][2]
			plyArray[plyIndex][6] = searchTime
			arrayIndex += 1
			plyIndex += 1
			plyArray.append([0,0,0,0,0,0,0])
		else: 
			arrayIndex += 1
		if arrayIndex == trajLineCount-1:
			found = 1
initUTM = initUTM.strip()

g = 1

print 'g, skipNum: ', g, skipNum

totalPoints = 1

print 'plyIndex: ', plyIndex

for i in range(12,plyIndex):
	if float(g) > float(skipNum):
		totalPoints += 1
		g = 0
	g += 1

totalPoints = totalPoints - 1
print 'totalPoints: ', totalPoints

gpsOutFileName = ('%sGPS_point_pairs_%s.ply' % (pathName, nowTime))
plyOutFile = open(gpsOutFileName,'w')
plyOutFile.write('ply\nformat ascii 1.0\ncomment UTM Zone %s GPS Offsets X %10.3f Y %10.3f Z %7.3f\nelement vertex %d\n' % (initUTM, gpsArray[1][0], gpsArray[1][1], gpsArray[1][2], totalPoints))
plyOutFile.write('property float x\nproperty float y\nproperty float z\nproperty float GPS_x\nproperty float GPS_y\nproperty float GPS_z\nproperty double time\nend_header\n')   	

g = 1

for i in range(12,plyIndex):
	if float(g) > float(skipNum):
		plyOutFile.write("%f %f %f %f %f %f %f \n" % (plyArray[i][0], plyArray[i][1], plyArray[i][2], plyArray[i][3], plyArray[i][4], plyArray[i][5], plyArray[i][6]))		
		g = 0
	g += 1


plyOutFile.close()
    
