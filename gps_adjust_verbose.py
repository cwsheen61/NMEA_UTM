#
#	Revised November 27, 2017
#
#
#	Version 0.5 (pre release)
#
#	added print version name
#	added print the offsets after finding them
#	this is the version that spits out a ton of data on position, including pseudo UTM, true UTM and latitude and longitude
#

import math
import sys
import os


# Lat Long - UTM, UTM - Lat Long conversions

from math import pi, sin, cos, tan, sqrt

#LatLong- UTM conversion..h
#definitions for lat/long to UTM and UTM to lat/lng conversions
#include <string.h>

_deg2rad = pi / 180.0
_rad2deg = 180.0 / pi

_EquatorialRadius = 2
_eccentricitySquared = 3

_ellipsoid = [
              #  id, Ellipsoid name, Equatorial Radius, square of eccentricity
              # first once is a placeholder only, To allow array indices to match id numbers
              [ -1, "Placeholder", 0, 0],
              [ 1, "Airy", 6377563, 0.00667054],
              [ 2, "Australian National", 6378160, 0.006694542],
              [ 3, "Bessel 1841", 6377397, 0.006674372],
              [ 4, "Bessel 1841 (Nambia] ", 6377484, 0.006674372],
              [ 5, "Clarke 1866", 6378206, 0.006768658],
              [ 6, "Clarke 1880", 6378249, 0.006803511],
              [ 7, "Everest", 6377276, 0.006637847],
              [ 8, "Fischer 1960 (Mercury] ", 6378166, 0.006693422],
              [ 9, "Fischer 1968", 6378150, 0.006693422],
              [ 10, "GRS 1967", 6378160, 0.006694605],
              [ 11, "GRS 1980", 6378137, 0.00669438],
              [ 12, "Helmert 1906", 6378200, 0.006693422],
              [ 13, "Hough", 6378270, 0.00672267],
              [ 14, "International", 6378388, 0.00672267],
              [ 15, "Krassovsky", 6378245, 0.006693422],
              [ 16, "Modified Airy", 6377340, 0.00667054],
              [ 17, "Modified Everest", 6377304, 0.006637847],
              [ 18, "Modified Fischer 1960", 6378155, 0.006693422],
              [ 19, "South American 1969", 6378160, 0.006694542],
              [ 20, "WGS 60", 6378165, 0.006693422],
              [ 21, "WGS 66", 6378145, 0.006694542],
              [ 22, "WGS-72", 6378135, 0.006694318],
              [ 23, "WGS-84", 6378137, 0.00669438]
              ]

#Reference ellipsoids derived from Peter H. Dana's website-
#http://www.utexas.edu/depts/grg/gcraft/notes/datum/elist.html
#Department of Geography, University of Texas at Austin
#Internet: pdana@mail.utexas.edu
#3/22/95

#Source
#Defense Mapping Agency. 1987b. DMA Technical Report: Supplement to Department of Defense World Geodetic System
#1984 Technical Report. Part I and II. Washington, DC: Defense Mapping Agency

#def LLtoUTM(int ReferenceEllipsoid, const double Lat, const double Long,
#             double &UTMNorthing, double &UTMEasting, char* UTMZone)

def LLtoUTM(ReferenceEllipsoid, Lat, Long):
    
    #converts lat/long to UTM coords.  Equations from USGS Bulletin 1532
    #East Longitudes are positive, West longitudes are negative.
    #North latitudes are positive, South latitudes are negative
    #Lat and Long are in decimal degrees
    #Written by Chuck Gantz- chuck.gantz@globalstar.com
    
    a = _ellipsoid[ReferenceEllipsoid][_EquatorialRadius]
    eccSquared = _ellipsoid[ReferenceEllipsoid][_eccentricitySquared]
    k0 = 0.9996
    
    #Make sure the longitude is between -180.00 .. 179.9
    LongTemp = (Long+180.0)-int((Long+180.0)/360.0)*360.0-180.0 # -180.00 .. 179.9
    
    LatRad = Lat*_deg2rad
    LongRad = LongTemp*_deg2rad
    
    ZoneNumber = int((LongTemp + 180.0)/6.0) + 1
    
    if Lat >= 56.0 and Lat < 64.0 and LongTemp >= 3.0 and LongTemp < 12.0:
        ZoneNumber = 32
    
    # Special zones for Svalbard
    if Lat >= 72.0 and Lat < 84.0:
        if  LongTemp >= 0.0  and LongTemp <  9.0:ZoneNumber = 31
        elif LongTemp >= 9.0  and LongTemp < 21.0: ZoneNumber = 33
        elif LongTemp >= 21.0 and LongTemp < 33.0: ZoneNumber = 35
        elif LongTemp >= 33.0 and LongTemp < 42.0: ZoneNumber = 37
    
    LongOrigin = (ZoneNumber - 1)*6 - 180 + 3 #+3 puts origin in middle of zone
    LongOriginRad = LongOrigin * _deg2rad
    
    #compute the UTM Zone from the latitude and longitude
    UTMZone = "%d%c" % (ZoneNumber, _UTMLetterDesignator(Lat))
    
    eccPrimeSquared = (eccSquared)/(1-eccSquared)
    N = a/sqrt(1-eccSquared*sin(LatRad)*sin(LatRad))
    T = tan(LatRad)*tan(LatRad)
    C = eccPrimeSquared*cos(LatRad)*cos(LatRad)
    A = cos(LatRad)*(LongRad-LongOriginRad)
    
    M = a*((1
            - eccSquared/4
            - 3*eccSquared*eccSquared/64
            - 5*eccSquared*eccSquared*eccSquared/256)*LatRad
           - (3*eccSquared/8
              + 3*eccSquared*eccSquared/32
              + 45*eccSquared*eccSquared*eccSquared/1024)*sin(2*LatRad)
           + (15*eccSquared*eccSquared/256 + 45*eccSquared*eccSquared*eccSquared/1024)*sin(4*LatRad)
           - (35*eccSquared*eccSquared*eccSquared/3072)*sin(6*LatRad))
        
    UTMEasting = (k0*N*(A+(1-T+C)*A*A*A/6
                               + (5-18*T+T*T+72*C-58*eccPrimeSquared)*A*A*A*A*A/120)
                         + 500000.0)
           
    UTMNorthing = (k0*(M+N*tan(LatRad)*(A*A/2+(5-T+9*C+4*C*C)*A*A*A*A/24
                                               + (61
                                                  -58*T
                                                  +T*T
                                                  +600*C
                                                  -330*eccPrimeSquared)*A*A*A*A*A*A/720)))
           
    if Lat < 0:
        UTMNorthing = UTMNorthing + 10000000.0; #10000000 meter offset for southern hemisphere
    return (UTMZone, UTMEasting, UTMNorthing)


def _UTMLetterDesignator(Lat):
    #This routine determines the correct UTM letter designator for the given latitude
    #returns 'Z' if latitude is outside the UTM limits of 84N to 80S
    #Written by Chuck Gantz- chuck.gantz@globalstar.com
    
    if 84 >= Lat >= 72: return 'X'
    elif 72 > Lat >= 64: return 'W'
    elif 64 > Lat >= 56: return 'V'
    elif 56 > Lat >= 48: return 'U'
    elif 48 > Lat >= 40: return 'T'
    elif 40 > Lat >= 32: return 'S'
    elif 32 > Lat >= 24: return 'R'
    elif 24 > Lat >= 16: return 'Q'
    elif 16 > Lat >= 8: return 'P'
    elif  8 > Lat >= 0: return 'N'
    elif  0 > Lat >= -8: return 'M'
    elif -8> Lat >= -16: return 'L'
    elif -16 > Lat >= -24: return 'K'
    elif -24 > Lat >= -32: return 'J'
    elif -32 > Lat >= -40: return 'H'
    elif -40 > Lat >= -48: return 'G'
    elif -48 > Lat >= -56: return 'F'
    elif -56 > Lat >= -64: return 'E'
    elif -64 > Lat >= -72: return 'D'
    elif -72 > Lat >= -80: return 'C'
    else: return 'Z'    # if the Latitude is outside the UTM limits

#void UTMtoLL(int ReferenceEllipsoid, const double UTMNorthing, const double UTMEasting, const char* UTMZone,
#              double& Lat,  double& Long )

def UTMtoLL(ReferenceEllipsoid, northing, easting, zone):
    
    #converts UTM coords to lat/long.  Equations from USGS Bulletin 1532
    #East Longitudes are positive, West longitudes are negative.
    #North latitudes are positive, South latitudes are negative
    #Lat and Long are in decimal degrees.
    #Written by Chuck Gantz- chuck.gantz@globalstar.com
    #Converted to Python by Russ Nelson <nelson@crynwr.com>
    
    k0 = 0.9996
    a = _ellipsoid[ReferenceEllipsoid][_EquatorialRadius]
    eccSquared = _ellipsoid[ReferenceEllipsoid][_eccentricitySquared]
    e1 = (1-sqrt(1-eccSquared))/(1+sqrt(1-eccSquared))
    #NorthernHemisphere; //1 for northern hemispher, 0 for southern
    
    x = easting - 500000.0 #remove 500,000 meter offset for longitude
    y = northing
    
    ZoneLetter = zone[-1]
    ZoneNumber = int(zone[:-1])
    if ZoneLetter >= 'N':
        NorthernHemisphere = 1  # point is in northern hemisphere
    else:
        NorthernHemisphere = 0  # point is in southern hemisphere
        y -= 10000000.0         # remove 10,000,000 meter offset used for southern hemisphere
    
    LongOrigin = (ZoneNumber - 1)*6 - 180 + 3  # +3 puts origin in middle of zone
    
    eccPrimeSquared = (eccSquared)/(1-eccSquared)
    
    M = y / k0
    mu = M/(a*(1-eccSquared/4-3*eccSquared*eccSquared/64-5*eccSquared*eccSquared*eccSquared/256))
    
    phi1Rad = (mu + (3*e1/2-27*e1*e1*e1/32)*sin(2*mu)
               + (21*e1*e1/16-55*e1*e1*e1*e1/32)*sin(4*mu)
               +(151*e1*e1*e1/96)*sin(6*mu))
    phi1 = phi1Rad*_rad2deg;
   
    N1 = a/sqrt(1-eccSquared*sin(phi1Rad)*sin(phi1Rad))
    T1 = tan(phi1Rad)*tan(phi1Rad)
    C1 = eccPrimeSquared*cos(phi1Rad)*cos(phi1Rad)
    R1 = a*(1-eccSquared)/pow(1-eccSquared*sin(phi1Rad)*sin(phi1Rad), 1.5)
    D = x/(N1*k0)
   
    Lat = phi1Rad - (N1*tan(phi1Rad)/R1)*(D*D/2-(5+3*T1+10*C1-4*C1*C1-9*eccPrimeSquared)*D*D*D*D/24
										 +(61+90*T1+298*C1+45*T1*T1-252*eccPrimeSquared-3*C1*C1)*D*D*D*D*D*D/720)
    Lat = Lat * _rad2deg
   
    Long = (D-(1+2*T1+C1)*D*D*D/6+(5-2*C1+28*T1-3*C1*C1+8*eccPrimeSquared+24*T1*T1)
		   *D*D*D*D*D/120)/cos(phi1Rad)
    Long = LongOrigin + Long * _rad2deg
    return (Lat, Long)


trajCount = 0
pointCloudLoop = 0
running = "|/-\\|/-\\"


pcInFileName = raw_input('Input the point cloud file name: ')
pcInfileName = pcInFileName.strip()
pcInFileName = pcInFileName.replace('\'','')
pcInFileName = pcInFileName.replace(' ','')

print pcInFileName



inFile = open(pcInFileName,'r')

trajInFileName = pcInFileName.replace('pointcloud','trajectory',1)
trajFile = open(trajInFileName,'r')

gpsInFileName = raw_input('Input the GPS correction file name: ')

gpsInfileName = gpsInFileName.strip()
gpsInFileName = gpsInFileName.replace('\'','')
gpsInFileName = gpsInFileName.replace(' ','')
gpsFile = open(gpsInFileName, 'r')


strOutFile = pcInFileName.replace('pointcloud_', 'pointcloud_UTM_', 1)

strTrajFile = trajInFileName.replace('trajectory_', 'trajectory_UTM_', 1)

strGoogCSVFile = trajInFileName.replace('trajectory_', 'trajectory_CSV_', 1)

strGoogCSVFile = strGoogCSVFile.replace('ply','csv',1)


pcOutFile = open(strOutFile,'w')
trajOutFile = open(strTrajFile,'w')
googOutFile = open(strGoogCSVFile,'w')

googOutFile.write('PointName, Latitude, Longitude\n')

hasRange = False

while True:
	headerLine = inFile.readline()
	if 'end_header' in headerLine:
		pcOutFile.write ('property float Easting\n')
		pcOutFile.write ('property float Northing\n')
		pcOutFile.write ('property int UTM_Zone_num\n')
		pcOutFile.write ('property int UTM_ZONE_Alph\n')
		pcOutFile.write ('property float Longitude\n')
		pcOutFile.write ('property float Latitude\n')
		pcOutFile.write ('property float trajectory_x\n')
		pcOutFile.write ('property float trajectory_y\n')
		pcOutFile.write ('property float trajectory_z\n')
		pcOutFile.write ('property float trajectory_roll\n')
		pcOutFile.write ('property float trajectory_pitch\n')
		pcOutFile.write ('property float trajectory_yaw\n')
		pcOutFile.write ('property float trajectory_time\n')
		pcOutFile.write ('property float trajectory_Easting\n')
		pcOutFile.write ('property float trajectory_Northing\n')
		pcOutFile.write ('property int trajectory_UTM_Zone_num\n')
		pcOutFile.write ('property int trajectory_UTM_ZONE_Alph\n')
		pcOutFile.write ('property float trajectory_Longitude\n')
		pcOutFile.write ('property float trajectory_Latitude\n')
		pcOutFile.write (headerLine)
		break
	else:
		pcOutFile.write(headerLine)
		if 'element' in headerLine:
			inStr = headerLine.split(' ')
			numPts = long(inStr[2])
		if 'point_range' in headerLine:
			hasRange = True
			
		



# print headerLine1, headerLine2, headerLine3, headerLine9

while True:
	trajLine = trajFile.readline()
	if 'end_header' in trajLine:
		trajOutFile.write ('property float Easting\n')
		trajOutFile.write ('property float Northing\n')
		trajOutFile.write ('property int UTM_Zone_num\n')
		trajOutFile.write ('property int UTM_Zone_Alpha\n')
		trajOutFile.write ('property float Longitude\n')
		trajOutFile.write ('property float Latitude\n')
		trajOutFile.write (trajLine)
		break

	else:
		trajOutFile.write(trajLine)
		if 'element' in trajLine:
			inStr = trajLine.split(' ')
			trajNumPts = long(inStr[2])

print 'Point cloud points: ', numPts

print 'Trajectory points: ', trajNumPts

gpsLine1 = gpsFile.readline()
gpsLine2 = gpsFile.readline()
gpsLine3 = gpsFile.readline()

#print (gpsLine1)
#print (gpsLine2)
#print (gpsLine3)

spaces = gpsLine3.count(" ")

gs = gpsLine3.split(' ',spaces + 1)

zone = gs[3]
xOffset = float(gs[7])
yOffset = float(gs[9])
zOffset = float(gs[spaces])

print 'xOffset = ', xOffset, ' yOffset = ', yOffset, ' zOffset = ', zOffset

trajStartIndex = 0
trajEndIndex = 0
lastTrajCount = 0

total = 0

skipPoints = 10
j = skipPoints
index = 0

while True:
	trajLine = trajFile.readline()
	if  not trajLine:
		break
	else:
		inStr = trajLine.split()
		trajX = float(inStr[0])
		trajY = float(inStr[1])
		trajZ = float(inStr[2])
		trajRoll = float(inStr[3])
		trajPitch = float(inStr[4])
		trajYaw = float(inStr[5])
		trajTime = float(inStr[6])
	
	trajX += xOffset
	trajY += yOffset
	trajZ += zOffset
	
	(trajLat, trajLon) = UTMtoLL(23, trajY, trajX, zone)
	(z, e, n) = LLtoUTM(23, trajLat, trajLon)
	sys.stdout.write('\rIndex: %d' % index)
	sys.stdout.flush()
	zAlpha = z[2]
	if zAlpha == 'A': zCode = 1
	elif zAlpha == 'B': zCode = 2
	elif zAlpha == 'C': zCode = 3
	elif zAlpha == 'D': zCode = 4
	elif zAlpha == 'E': zCode = 5
	elif zAlpha == 'F': zCode = 6
	elif zAlpha == 'G': zCode = 7
	elif zAlpha == 'H': zCode = 8
	elif zAlpha == 'I': zCode = 9
	elif zAlpha == 'J': zCode = 10
	elif zAlpha == 'K': zCode = 11
	elif zAlpha == 'L': zCode = 12
	elif zAlpha == 'M': zCode = 13
	elif zAlpha == 'N': zCode = 14
	elif zAlpha == 'O': zCode = 15
	elif zAlpha == 'P': zCode = 16
	elif zAlpha == 'Q': zCode = 17
	elif zAlpha == 'R': zCode = 18
	elif zAlpha == 'S': zCode = 19
	elif zAlpha == 'T': zCode = 20
	elif zAlpha == 'U': zCode = 21
	elif zAlpha == 'V': zCode = 22
	elif zAlpha == 'W': zCode = 23
	elif zAlpha == 'X': zCode = 24
	elif zAlpha == 'Y': zCode = 25
	elif zAlpha == 'Z': zCode = 26
	zVal= '%s%s' % (z[0],z[1])
	trajOutFile.write("%f %f %f %f %f %f %f %f %f %s %d %f %f\n" % (trajX, trajY, trajZ, trajRoll, trajPitch, trajYaw, trajTime, e, n, zVal, zCode, trajLon, trajLat))
	if j == skipPoints:
		googOutFile.write("Point:%d,%12.8f,%12.8f\n" % (index, trajLat, trajLon))
		j = 0
		index += 1
	j += 1
trajOutFile.close()
googOutFile.close()

sys.stdout.write('\n')
sys.stdout.flush()

i = 0
index = 0
trTime = -20.0

while True:
	inLine = inFile.readline()
	if not inLine:
		break
	inStr = inLine.split()
	cloudX = float(inStr[0])
	cloudY = float(inStr[1])
	cloudZ = float(inStr[2])
	cloudInt = float(inStr[3])
	if hasRange:
		pointRange = float(inStr[4])
		pointTime = float(inStr[5])
	else:
		pointTime = float(inStr[4])

	
	cloudX += xOffset
	cloudY += yOffset
	cloudZ += zOffset
	
	(cloudLat, cloudLon) = UTMtoLL(23, cloudY, cloudX, zone)
	(z, e, n) = LLtoUTM(23, cloudLat, cloudLon)
	zAlpha = z[2]
	if zAlpha == 'A': zCode = 1
	elif zAlpha == 'B': zCode = 2
	elif zAlpha == 'C': zCode = 3
	elif zAlpha == 'D': zCode = 4
	elif zAlpha == 'E': zCode = 5
	elif zAlpha == 'F': zCode = 6
	elif zAlpha == 'G': zCode = 7
	elif zAlpha == 'H': zCode = 8
	elif zAlpha == 'I': zCode = 9
	elif zAlpha == 'J': zCode = 10
	elif zAlpha == 'K': zCode = 11
	elif zAlpha == 'L': zCode = 12
	elif zAlpha == 'M': zCode = 13
	elif zAlpha == 'N': zCode = 14
	elif zAlpha == 'O': zCode = 15
	elif zAlpha == 'P': zCode = 16
	elif zAlpha == 'Q': zCode = 17
	elif zAlpha == 'R': zCode = 18
	elif zAlpha == 'S': zCode = 19
	elif zAlpha == 'T': zCode = 20
	elif zAlpha == 'U': zCode = 21
	elif zAlpha == 'V': zCode = 22
	elif zAlpha == 'W': zCode = 23
	elif zAlpha == 'X': zCode = 24
	elif zAlpha == 'Y': zCode = 25
	elif zAlpha == 'Z': zCode = 26
	
	zVal= '%s%s' % (z[0],z[1])

	tr = open(strTrajFile,'r')
	if trTime != pointTime:
		while True:
			trLine = tr.readline()
			if 'end_header' in trLine: break
	
		while True:
			trLine = tr.readline()
			if not trLine: break
			trLine = trLine.strip()
			inStr = trLine.split()
			trTime = inStr[6]
			if trTime >= pointTime: break		
		

	if hasRange:
		pcOutFile.write("%f %f %f %f %f %f %f %f %s %d %f %f %s\n" % (cloudX, cloudY, cloudZ, cloudInt, pointRange, pointTime, e, n, zVal, zCode, cloudLon, cloudLat, trLine))
	else:
		pcOutFile.write("%f %f %f %f %f %f %f %s %d %f %f %s\n" % (cloudX, cloudY, cloudZ, cloudInt, pointTime, e, n, zVal, zCode, cloudLon, cloudLat, trLine))	
	if float(index/1000000) == float(index)/1000000.0:
			sys.stdout.write('\rpoints: %d' % index)
			sys.stdout.flush()
	index += 1	
	


pcOutFile.close()
