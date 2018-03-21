import math
import sys
import os


trajCount = 0
pointCloudLoop = 0
running = "|/-'\'|/-'\'"


pcInFileName = sys.argv[1]
inFile = open(pcInFileName,'r')

trajInFileName = sys.argv[2]
trajFile = open(trajInFileName,'r')

gpsInFileName = sys.argv[3]
gpsFile = open(gpsInFileName, 'r')
# 


strOutFile = pcInFileName.replace('pointcloud_', 'pointcloud_UTM_', 1)



strTrajFile = trajInFileName.replace('trajectory_', 'trajectory_UTM_', 1)





pcOutFile = open(strOutFile,'w')
trajOutFile = open(strTrajFile,'w')



headerLine1 = inFile.readline()
headerLine2 = inFile.readline()
headerLine3 = inFile.readline()
headerLine4 = inFile.readline()
headerLine5 = inFile.readline()
headerLine6 = inFile.readline()
headerLine7 = inFile.readline()
headerLine8 = inFile.readline()
headerLine9 = inFile.readline()
headerLine10 = inFile.readline()

pcOutFile.write(headerLine1)
pcOutFile.write(headerLine2)
pcOutFile.write(headerLine3)
pcOutFile.write(headerLine4)
pcOutFile.write(headerLine5)
pcOutFile.write(headerLine6)
pcOutFile.write(headerLine7)
pcOutFile.write(headerLine8)
pcOutFile.write(headerLine9)
pcOutFile.write(headerLine10)


# print headerLine1, headerLine2, headerLine3, headerLine9

trajLine1 = trajFile.readline()
trajLine2 = trajFile.readline()
trajLine3 = trajFile.readline()
trajLine4 = trajFile.readline()
trajLine5 = trajFile.readline()
trajLine6 = trajFile.readline()
trajLine7 = trajFile.readline()
trajLine8 = trajFile.readline()
trajLine9 = trajFile.readline()
trajLine10 = trajFile.readline()
trajLine11 = trajFile.readline()
trajLine12 = trajFile.readline()

trajOutFile.write (trajLine1)
trajOutFile.write (trajLine2)
trajOutFile.write (trajLine3)
trajOutFile.write (trajLine4)
trajOutFile.write (trajLine5)
trajOutFile.write (trajLine6)
trajOutFile.write (trajLine7)
trajOutFile.write (trajLine8)
trajOutFile.write (trajLine9)
trajOutFile.write (trajLine10)
trajOutFile.write (trajLine11)
trajOutFile.write (trajLine12)

str1, str2, strNumPts = headerLine4.split(' ',3)

numPts = int(strNumPts)

#print numPts

str1, str2, strTrajNumPts = trajLine4.split(' ',3)

trajNumPts = int(strTrajNumPts)

#print trajNumPts

gpsLine1 = gpsFile.readline()
gpsLine2 = gpsFile.readline()
gpsLine3 = gpsFile.readline()

#print (gpsLine1)
#print (gpsLine2)
#print (gpsLine3)

spaces = gpsLine3.count(" ")

gs = gpsLine3.split(' ',spaces + 1)

xOffset = float (gs[7])
yOffset = float (gs[9])
zOffset = float (gs[spaces])

trajArray = [[0.0 for x in range(7)] for y in range(trajNumPts)]
trajStartIndex = 0
trajEndIndex = 0
lastTrajCount = 0

total = 0


for index in range (trajNumPts+1):
	trajInLine = trajFile.readline()
	if trajInLine <> "":
		strX, strY, strZ, strR, strP, strYaw, strTime = trajInLine.split(' ',7)
		trajX = float(strX)
		trajY = float(strY)
		trajZ = float(strZ)
		trajRoll = float(strR)
		trajPitch = float(strP)
		trajYaw = float(strYaw)
		trajTime = float(strTime)
	else: break
	
	trajX += xOffset
	trajY += yOffset
	trajZ += zOffset
#	print (index)
	trajOutFile.write("%14.6f %14.6f %14.6f %14.6f %14.6f %14.6f %20.6f \n" % (trajX, trajY, trajZ, trajRoll, trajPitch, trajYaw, trajTime))
	
trajOutFile.close()
i = 0
for index in range(numPts+1):
	inLine = inFile.readline()
	if inLine == "":
		break
	str1, str2, str3, str4, str5 = inLine.split(' ',5)
	cloudX = float(str1)
	cloudY = float(str2)
	cloudZ = float(str3)
	cloudInt = float(str4)
	pointTime = float(str5)

	
	cloudX += xOffset
	cloudY += yOffset
	cloudZ += zOffset
	pcOutFile.write("%14.6f %14.6f %14.6f %14.6f %20.6f\n" % (cloudX, cloudY, cloudZ, cloudInt, pointTime))
	if float(index/10000) == float(index)/10000.0:
			sys.stdout.write(' %s\r' % running[i])
			sys.stdout.flush()
			i += 1
			if i == 8: i = 0
		
	


pcOutFile.close()
