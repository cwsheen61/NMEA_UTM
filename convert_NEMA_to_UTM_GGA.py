#!/usr/bin/env python

# 	convert_NEMA_to_UTM.py
#	version 0.5
#	1 December 2017
#	
#	moved skipping step to create_gps_ply.py
# 	


import sys
import os
from datetime import datetime
import datetime
from time import gmtime, strftime


print 'convert_NEMA_to_UTM.py version 0.5, pre-release, 1 December 2017'
print 'written by C. Wade Sheen, Kaarta'
print 'copyright 2017 by Kaarta'


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
#			 double &UTMNorthing, double &UTMEasting, char* UTMZone)

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
    else: return 'Z'	# if the Latitude is outside the UTM limits

#void UTMtoLL(int ReferenceEllipsoid, const double UTMNorthing, const double UTMEasting, const char* UTMZone,
#			  double& Lat,  double& Long )

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

def heap_sort(items):
	heapq.heapify(items)
	items[:] = [heapq.heappop(items) for i in range(len(items))]


#if len(sys.argv) < 4:
#	print ("Usage: python %s '</path/to/gps_log_file.ext>' grid_size skip_num" % sys.argv[0])
#	exit (0)



#gpsLogFileName = sys.argv[1]
#grid = float(sys.argv[2])
#trajFileName = sys.argv[3]
#maxHDOP = float(sys.argv[4])
#nowTime = sys.argv[5]

gpsLogFileName = input('gpsLogFileName: ')
grid = float(input('Grid size: '))
trajFileName = input('Trajectory file name: ')
maxHDOP = float(input('MaxHdop: '))
nowTime = "00-00-00-00-00-00"
pathName, tail = os.path.split(trajFileName)

slash = "/"

pathName = ('%s%s' % (pathName, slash))

print pathName


lastTime = os.path.getmtime(trajFileName)

fileDay=int(datetime.datetime.utcfromtimestamp(lastTime).strftime('%d'))
fileMonth=int(datetime.datetime.utcfromtimestamp(lastTime).strftime('%m'))
fileYear=int(datetime.datetime.utcfromtimestamp(lastTime).strftime('%Y'))


print ('Date of Aquisition: %2d/%2d/%4d (dd,mm,yy)' % (fileDay, fileMonth, fileYear))


gpsOutFileName = '%sgps_parsed_%s.txt' % (pathName, nowTime)

# print gpsOutFileName

gpsLogFile = open(gpsLogFileName,'r')
gpsOutFile = open(gpsOutFileName,'w')
#timeOutFile = open('testtime.txt', 'w')

gpsMatrix = [[0.0 for x in range(10)] for y in range(1)]

lineCount = 0
minHDOP = 100.0

firstCrossN = 0
firstCrossE = 0

for gpsLogStr in gpsLogFile:
#	print ('Line: %d, String: %s' % (lineCount, gpsLogStr))
	typeStr = gpsLogStr.split (",",1)
#	print typeStr
	
	if "GGA" in typeStr[0]:
		print typeStr[0]
		commas = gpsLogStr.count(',')
		typeStr = gpsLogStr.split(',',commas+1)
#		0:type,  1:time,      2:lat,      3:N/S, 4:long,      5:E/W, 6:Fix, 7:numSats, 8:HDOP, 9:Elev, 10:units, 11:geoid,  12:units, 13:DGPS, 14:chkSum 
#         $GPGGA,  062640.600,  1646.3555,  N,     07800.1317,  E,     1,     06,        1.5,    504.4,   M,        -73.3,     M,         ,       0000*79
		gpsTime = float(typeStr[1])
		gpsHour = int(gpsTime/10000)
		gpsMin = int((gpsTime-gpsHour*10000)/100)
		gpsSecDec = gpsTime-(gpsHour*10000)-(gpsMin*100)
		gpsSec = int(gpsSecDec)
		gpsuSec = int((gpsSecDec - gpsSec) * 1000000.0)
		
		localTimeStr = datetime.datetime(fileYear, fileMonth, fileDay, gpsHour, gpsMin, gpsSec, gpsuSec)
#		print localTimeStr
		
		localTime = float(localTimeStr.strftime("%s.%f"))
		deltatime = float(datetime.datetime.utcnow().strftime("%s.%f")) - float(datetime.datetime.now().strftime("%s.%f"))
		
		
		gpsTime = localTime-deltatime
		
#		gpsTime = gpsTime + (5.5 * 3600)
#		timeOutFile.write("%f\n" % gpsTime)
#		print (gpsTime)
#		print 'typeStr: ', typeStr
		if typeStr[2] <> '':
			gpsLat = float(typeStr[2])
			if typeStr[3] == 'S': gpsLat=gpsLat*-1
			gpsAlt = float(typeStr[9])
			gpsGeoid = float(typeStr[11])
			gpsAlt = gpsAlt - gpsGeoid
			if typeStr[8] <> "": gpsHDOP = float(typeStr[8]) 
			else: gpsHDOP = -1
			if gpsHDOP < minHDOP: minHDOP = gpsHDOP
			gpsLon = float(typeStr[4])
			if typeStr[5] == 'W': gpsLon = -1 * gpsLon
			lonDeg = float(int(gpsLon/100))
			lonRem = (gpsLon - 100.0*lonDeg)/60.0
			latDeg = float(int(gpsLat/100))
			latRem = (gpsLat - 100.0*latDeg)/60.0
			latDeg = latDeg + latRem
			lonDeg = lonDeg + lonRem
#		print gpsLat, gpsLon
#		print latDeg, lonDeg
#		print ('Line: %d, String: %s' % (lineCount, typeStr[0]))

#			Lat = latDeg
#			Long = lonDeg
			ellipsoid = 23
#		23 = WGS-84
			(z, e, n) = LLtoUTM (ellipsoid, latDeg, lonDeg)
#		print z, e, n
			zInt = int(10 * float(z[0]) + float(z[1]))
			zAlpha = z[2]
			if lineCount == 0:
				zOrig = zInt
				zAlphaOrig = zAlpha
				zStart = z
			lineCount += 1
			if zInt == zOrig:
				if zAlpha == zAlphaOrig:
					lastN = n
				else:
					if firstCrossN == 0:
						deltaN = n - lastN
						n = n - deltaN
						firstCrossN = 1
					else:
						n  = n-deltaN
				lastE = e
			else:
				if firstCrossE == 0:
					deltaE = e - lastE
					e = e - deltaE
					firstCrossE = 1
				else:
					e = e - deltaE
						
			gpsOutFile.write('%f %f %f %f %f %s\n' % (e, n, gpsAlt, gpsHDOP, gpsTime, z))

gpsOutFile.close()

f = open(gpsOutFileName,'r')

i = 0
j = 0

for inString in f:
	eastStr, northStr, altStr, HDOPStr, timeStr, zStr = inString.split(" ",6)
	east = float (eastStr)
	north = float (northStr)
#	print north
	alt = float(altStr)
	HDOP = float (HDOPStr)
	time = float (timeStr)
	z = zStr.strip()
	zoneInt = 10*float(z[0])+float(z[1])
	zoneAlpha = z[2]
	gpsMatrix [i][0] = east
	gpsMatrix [i][1] = north
	gpsMatrix [i][2] = alt
	gpsMatrix [i][3] = HDOP
	gpsMatrix [i][4] = time
	gpsMatrix [i][5] = z
	gpsMatrix [i][9] = i
	gpsMatrix.append([0,0,0,0,0,0,0,0,0,0])
#	print i
	i += 1

numPts = i
count = 0
sumAlt = 0.0

for j in range(numPts):
	for k in range(numPts):
		if sqrt((gpsMatrix[j][0]-gpsMatrix[k][0])**2 + (gpsMatrix[j][1]-gpsMatrix[k][1])**2)<= grid:
			sumAlt += gpsMatrix[k][2]
			count +=1
	gpsMatrix[j][6] = sumAlt / float(count)
	count = 0
	sumAlt = 0.0
#	if float(j)/100.0 == float((j/100)): 
#		sys.stdout.write('.')
#		sys.stdout.flush()

#print'.'
	
secondFile = '%sgps_trajectory_matched_%s.txt' % (pathName , nowTime)

f2 = open(secondFile,'w')

f2.write ('Easting Northing Elevation Elv_Correction HDOP Time(s) UTM_zone\n')

for j in range(numPts):
	if gpsMatrix [j][3] <= maxHDOP:
		f2.write('%f %f %f %f %f %f %s\n' % (gpsMatrix[j][0], gpsMatrix[j][1], gpsMatrix[j][6], (gpsMatrix[j][6]-gpsMatrix[j][2]), gpsMatrix[j][3], gpsMatrix[j][4], gpsMatrix[j][5]))


f2.close()

	
	
	
	

	


	



	
		
