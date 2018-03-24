import sys

pcFile = raw_input('Input the file name: ')
pcFile = pcFile.strip()
pcFile = pcFile.replace('\'','')
pcFile = pcFile.replace(' ','')

p = open(pcFile,'r')

lineCount = 0

while True:
	pLine = p.readline()
	if not pLine: break
	if 'elemen' in pLine:
		s = pLine.split()
		points = long(s[2])
	if 'end_header' in pLine: break

print ('Points: %d' % points)

while True:
	pLine = p.readline()
	if not pLine: break
	lineCount += 1
	if float(lineCount/100000) == float(lineCount)/100000.0:
		sys.stdout.write('\rlines: %d' % lineCount)
		sys.stdout.flush()

print ('lines = %d ' % lineCount)


