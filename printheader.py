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
	print pLine.strip()
	if 'end_header' in pLine: break

