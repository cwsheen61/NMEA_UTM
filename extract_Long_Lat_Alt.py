pcFileName = raw_input('Input the point cloud filename with Longitude, Latitude and Altitude info: ')
pcInName = pcFileName.strip()
pcInName = pcInName.replace('\'','',)
pcOutName = pcInName.replace('.ply','.csv',1)
p = open(pcInName,'r')
out = open(pcOutName,'w')

for line in p:
	print line
	if line == 'end_header\n':
		break

for line in p:
	inStr = line.split(' ')
	out.write('%s, %s, %s\n' % (inStr[9], inStr[10].strip(), inStr[2]))

p.close()
out.close()


