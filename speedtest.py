
#!/usr/bin/python
from Adafruit_MCP4725 import MCP4725
import time
import math
import os
os.system('modprobe i2c_bcm2708 baudrate=800000')
def lev(V):
	return int(round(V/5.0*4095))

mode = 2;
       #mode 8 fails, takes 180 us to set both voltages, galvo cant move fast enough either
	# mode 1 alternates between 2 points, usually perfectly centered "ON" and off the sample, "OFF" with a certain period
	# mode 2 is x centeres and norastered profiles
	# mode 5 is single point
	# mode 6 is rastered profile
	# 9 is for nonrastered y profiles taht skip the Y center until last to reduce bleaching in PEO

#CONSTANTS THAT COULD CAHNGE AS SETUP CHANGES

#NOT EXPANDED
#centerY = 2.2576; #V PMMA 7-3a-1 1/26/18
#centerX = 2.5556; #  bare epoxy s1 1/30/18 as well

#centerY = 2.2576;  #  2x glass Epoxy 2/1/2018 due to increased thickness of glass?
#centerX = 2.4774;  #    but y direction stays cause angles are less extreme

#centerY = 2.2576;   #  2x epoxy epoxy 2/5/2018 
#centerX = 2.4994;   #    y direction still same

#centerX = 2.5004;   # 2x glass epoxy x center 2-12 higher power
#centerY = 2.3028;   #

#centerX = 2.5849; # 2x coverslip epoxy x center 2-19 
#centerY = 2.3053; #

#centerX = 2.5153; # 2x epoxy epoxy x center 2-23 
#centerY = 2.3320; #

centerX = 2.5260; # 2x Sapphire epoxy x center 2-26 
centerY = 2.3458; #



#EXPANDED
#centerY = 2.956;
#centerX = 2.53;


voltageToPositionX = 4.12; # mm/V
voltageToPositionY = 3.52; # mm/V
laserSpotRadius = 0.949; #mm unexpanded


dac=MCP4725(0x62)
dacY=MCP4725(0x63)
x=0

try:
	if mode==1:
		# Goes from 0,0 to a point (x,y) in one move, then waits, then moves back
		
		#1) generate list of points (this will change depending on what we want to do)
		#xlist
		#xlist=[lev(centerX-0.50),lev(centerX-0.25),lev(centerX),lev(centerX+0.25),lev(centerX+0.50)]
		xlist=[]
		for b in range(-4,5):
			xlist.append(lev(centerX+b/2.0))
			print(centerX+b/2.0)
		#ylist
		#ylist=[lev(centerY-0.50),lev(centerY-0.25),lev(centerY),lev(centerY+0.25),lev(centerY+0.50)]
		ylist=[]
		for b in range(-4,5):
			ylist.append(lev(centerY+b/2.0))	
			print(centerY+b/2.0)

		dac.setVoltage(lev(0))
		dac.setVoltage(lev(0))
		dacY.setVoltage(lev(0))
		dacY.setVoltage(lev(0))
		begin = time.time()
		sleep_timer = 1000;
		repetition_num = 2;
		switchtime = begin+sleep_timer
		position = True;
		for xpoint in xlist:
			for ypoint in ylist:
				for n in range(0,repetition_num):
					switch=position
					while(switch==position):
						if (time.time()>switchtime):
							if position:
								with open('writtenvoltageX.txt','w') as f:
									f.write(str(xpoint))
								with open('writtenvoltage.txt','w') as f:
									f.write(str(ypoint))
								print("laser ON "+str(xpoint)+" "+str(ypoint))
								dac.setVoltage(xpoint)
								dac.setVoltage(xpoint)
								dacY.setVoltage(ypoint)
								dacY.setVoltage(ypoint)
							else:
								with open('writtenvoltageX.txt','w') as f:
									f.write(str(0))
								with open('writtenvoltage.txt','w') as f:
									f.write(str(0))
								print("laser      OFF")
								dac.setVoltage(4095)
								dac.setVoltage(4095)
								dacY.setVoltage(4095)
								dacY.setVoltage(4095)
							position = not(position)
							switchtime = time.time()+sleep_timer
						time.sleep(0.2)
					
			
	elif mode ==2:
		# 1d straight line
		#period = 1/25.0   #in seconds forline rastered heatups
		#period = 1800
		period = 5017.331*3.0 # in seconds for nonrastered profiles
		writeFlag = True
		#t_interval = .05 #deprecated?
		t_min = .0333 #"avg" maximum update speed of RPi 
		#t_interval = max(period/(2*4096), t_min)
		#numpts = int(period/t_interval)
		#minX = 0.0
		#maxX = 4.998
		minX = centerY-0.3 #for center searches
		maxX = centerY+0.3 #for center searches
		#minX = centerX-0.3 #for center searches
		#maxX = centerX+0.3 #for center searches
		deltaX = maxX-minX
		t_interval = max(period/(2*lev(deltaX)),t_min)
		numpts = int(period/t_interval)
		incx = deltaX/(numpts/2)
		list = []
		iX = -deltaX
		print 1/period, t_interval,numpts, minX, maxX, deltaX, incx, iX
		while iX < deltaX:
			list.append(lev(abs(iX)+minX))
			iX = iX + incx	
		#print list

		pointX = lev(centerX)
		pointY = lev(centerY)
		pointStatic = pointX
		dac.setVoltage(pointStatic)
		#dacY.setVoltage(pointStatic)
		with open('writtenvoltageX.txt','w') as f:
			f.write(str(pointStatic))
		#print len(list),numpts

		while(True):
			begin = time.time()
			timer= time.time() +period
			file_write_timer = begin + 5
			while time.time() < timer:
				point = int((time.time()-begin)/t_interval) % numpts
				dacY.setVoltage(list[point])
				#dac.setVoltage(list[point])
				current_time = time.time()
				if writeFlag & (current_time > file_write_timer):
					with open('writtenvoltage.txt','w') as f:
						f.write(str(list[point]))
					file_write_timer = current_time + 5

	elif mode ==3:
		pattern = file('ncsuraster.txt','r')
		patternlist=eval(pattern.read())
		while (True):
			for pair in patternlist:
				dac.setVoltage(int(pair[0]/2))
				dacY.setVoltage(int(pair[1]/2))
	elif mode ==4:
		#raster L shape with corner on centerX and centerY
		#make pattern
		period = 1/25.0;
		t_interval = .000333
		numpts = int(period/t_interval)
		l=[]
		minX= centerX
		maxX = minX + 2.5
		minY= centerY
		maxY = minY-2.5
		incX = (maxX-minX)/(numpts/4)
		incY = (maxY-minY)/(numpts/4)
		iX=minX
		iY=minY
		while iX<(maxX):
			l.append([lev(round(iX,5)),lev(minY)])
			iX=iX+incX
		iX=maxX-incX/2
		while iX > (minX+incX/4):
			l.append([lev(round(iX,5)),lev(minY)])
			iX=iX-incX
		while iY>(maxY):
			l.append([lev(minX),lev(round(iY,5))])
			iY=iY+incY
		iY=maxY-incY/2
		while iY < (minY+incY/4):
			l.append([lev(minX),lev(round(iY,5))])
			iY=iY-incY
		#run pattern
		while (True):
			timer = time.time()
			#for pair in l:
			#	dac.setVoltage(lev(pair[0]))
			#	dacY.setVoltage(lev(pair[1]))
			#	#print "%.7f" % time.time(
			while (time.time() < timer+period):
				point = int((time.time()-timer)/t_interval %numpts)
				pair = l[point]
				dac.setVoltage(pair[0])
				dacY.setVoltage(pair[1])


	elif mode ==5:
		#set to single point
		dac.setVoltage(lev(centerX))
		dacY.setVoltage(lev(centerY))
		while True:
			time.sleep(1)
	elif mode == 6:
		#periody = 5017.34/3.0
		periody = 15.0
		wait_flag = False
		wait_length = 500 
		t_interval = .000333
		t_intervaly = max(periody/(2*4096),0.000333)
		periodx = 1/25.0  #'x' direction is fast direction
		numptsx = int(periodx/t_interval)
		### normmal operation 'x' is fast direction
		maxX = 4.5
		minX = 0.0
		## change for lower power x center 2017-2-17
		#maxX = 2.6
		#minX = 2.4
		deltax = maxX-minX
		incx = float(deltax)/(numptsx/2)
		listX = []
		iX = -deltax
		while iX < deltax:
			listX.append(lev(abs(iX)+minX))
			iX = iX+incx
		numptsy = int(periody/t_intervaly)
		# for regular
		#maxY = centerY+0.85
		#minY = centerY-0.85
		# for x direction as slow
		#maxY = centerX+0.85
		#minY = centerX-0.85
		# for ful range
		maxY = 4.5
		minY = 0

		deltay = maxY-minY
		incy = float(deltay)/(numptsy/2)
		listY = []
		iY = -deltay
		while iY < deltay:
			listY.append(lev(abs(iY)+minY))
			iY = iY+incy
		begin = time.time()
		file_write_timer = begin+5
		#print file_write_timer
		wait_timer = begin+1.2*periody
		print begin, periodx, periody, t_interval, t_intervaly
		while(True):
			pointx = int((time.time()-begin)/t_interval) % numptsx
			pointy = int((time.time()-begin)/t_intervaly) % numptsy
			#print pointx, pointy, listX[1],listY[1]
			#dacY.setVoltage(listY[pointy])
			#dac.setVoltage(listX[pointx])
			# switched so taht x direction is slow
			dac.setVoltage(listY[pointy])
			dacY.setVoltage(listX[pointx])
			current_time = time.time()
			#print current_time, file_write_timer
			if current_time >file_write_timer:
				with open('writtenvoltageX.txt','w') as f:
					f.write(str(listX[pointx]))
				with open('writtenvoltage.txt','w') as f:
					f.write(str(listY[pointy]))
				#print str(listY[pointy])
				file_write_timer = time.time()+5
			if (wait_flag and (current_time > wait_timer)):
				dacY.setVoltage(0)
				dac.setVoltage(0)
				with open('writtenvoltage.txt','w') as f:
					f.write('0')
				time.sleep(wait_length)
				wait_timer = time.time()+1.2*periody



	elif mode == 7:
		# slowly wander a point in a grid, SLOWLY in both directions
		#make pattern
		#-----------------------------------------------------------
		wait_flag = 0
		wait_length = 500 
		t_interval = .0333
		t_intervaly = .00333


		#periodx = 1/25.0
		periodx = 15
		numptsx = int(periodx/t_interval)
		maxX = 4.98
		minX = 0.0
		#maxX = centerX+2
		#minX = centerX-2 
		deltax = maxX-minX
		incx = float(deltax)/(numptsx/2)
		listX = []
		iX = -deltax
		while iX < deltax:
			listX.append(lev(abs(iX)+minX))
			iX = iX+incx


		periody = 0.13
		numptsy = int(periody/t_intervaly)
		maxY = 4.98
		minY = 0.0
		#maxY = centerY+0.2
		#minY = centerY-0.2
		deltay = maxY-minY
		incy = float(deltay)/(numptsy/2)
		listY = []
		iY = -deltay
		while iY < deltay:
			listY.append(lev(abs(iY)+minY))
			iY = iY+incy
		begin = time.time()
		file_write_timer = begin+5
		wait_timer = begin+1.2*periody
		print begin, periodx, periody, t_interval
		while(True):
			pointx = int((time.time()-begin)/t_interval) % numptsx
			pointy = int((time.time()-begin)/t_intervaly) % numptsy
			#print pointx, pointy, listX[1],listY[1]
			dacY.setVoltage(listY[pointy])
			dac.setVoltage(listX[pointx])
			current_time = time.time()
			if current_time >file_write_timer:
				with open('writtenvoltage.txt','w') as f:
					f.write(str(listY[pointy]))
				with open('writtenvoltageX.txt','w') as f:
					f.write(str(listX[pointx]))
				file_write_timer = time.time()+5
			if (wait_flag and (current_time > wait_timer)):
				dacY.setVoltage(0)
				dac.setVoltage(0)
				with open('writtenvoltage.txt','w') as f:
					f.write('0')
				time.sleep(wait_length)
				wait_timer = time.time()+1.2*periody
	
	elif mode == 8 :
		#simulate a rastered line in that it heats asampling  point only during 
		# the time that a rastered point would be on that point
		# but instead of moving the laser to other parts of the 
		# specimen when not irradiating the sample point, move it off
		# the specimen entirely
		#   AKA blink on the sample point at the same rate that a 
		#    rastered line would, but dont heat non sampled areas
		simRasterPeriod = 1/5.0 #seconds in full triangle wave period
		simRasterLength_dV = 4.5 #full length of raster line to sim
		blinkPeriod = simRasterPeriod/2
		litFraction = laserSpotRadius*simRasterPeriod / (simRasterLength_dV*voltageToPositionX)		
		litTime = blinkPeriod*litFraction;
		centerLevX = lev(centerX) # galvo coord to heat
		centerLevY = lev(centerY) # ...samesies
		dumpLevXY = 4095; #where to send laser when not heating		
		while True:
			begin = time.time()
			dac.setVoltage(centerLevX)
			dacY.setVoltage(centerLevY)
			while time.time()-begin < litTime:
				time.sleep(.0001)
			dac.setVoltage(dumpLevXY)
			dacY.setVoltage(centerLevY)
			while time.time()-begin < blinkPeriod:
				time.sleep(.0001)

			
	elif mode == 9:
		# 1d straight line
		#period = 1/25.0 #in seconds
		period = 5017.33
		writeFlag = True
		#t_interval = .05 #desired interval
		t_min = .000333 #"avg" maximum update speed of RPi 
		t_interval = max(period/(2*4096), t_min)
		numpts = int(period/t_interval)
		minX = 0.0
		maxX = 4.5
		#minX = centerY-1.0
		#maxX = centerY+1.0
		#minX = centerX-1.0
		#maxX = centerX+1.0
		deltaX = maxX-minX
		incx = deltaX/(numpts/2)
		list = []
		iX = minX
		bufferX = 0.25
		print 1/period, t_interval, minX, maxX, deltaX, incx, iX
		#while iX < deltaX:
		#	list.append(lev(abs(iX)+minX))
		#	iX = iX + incx	
		while iX < (centerY - bufferX):
			list.append(lev(iX))
			iX = iX+incx
		iX = centerY + bufferX
		while iX < maxX:
			list.append(lev(iX))
			iX = iX+incx
		iX = maxX
		while iX >(centerY - bufferX):
			list.append(lev(iX))
			iX = iX - incx
		iX = centerY-bufferX
		while iX < (centerY+bufferX):
			list.append(lev(iX))		
			iX = iX+incx
		iX = centerY-bufferX
		while iX>minX:
			list.append(lev(iX))
			iX = iX-incx

		#print list
		pointX = lev(centerX)
		pointY = lev(centerY)
		#print len(list),numpts
		while(True):
			begin = time.time()
			timer= time.time() +period
			dac.setVoltage(pointX)
			#dacY.setVoltage(pointY)
			file_write_timer = begin + 5
			while time.time() < timer:
				point = int((time.time()-begin)/t_interval) % numpts
				dacY.setVoltage(list[point])
				#dac.setVoltage(list[point])
				current_time = time.time()
				if writeFlag & (current_time > file_write_timer):
					with open('writtenvoltage.txt','w') as f:
						f.write(str(list[point]))
					file_write_timer = current_time + 5


except KeyboardInterrupt:
	dac.setVoltage(4095)
	dacY.setVoltage(4095)


dac.setVoltage(4095)
dacY.setVoltage(4095)
