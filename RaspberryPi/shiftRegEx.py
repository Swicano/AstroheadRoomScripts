# Testing a shift register to replace the Parrallel port driver for the monochromator

import RPi.GPIO as GPIO
import time

latchPin = 15
clockPin = 18
dataPin = 14 
outEnablePin = 23

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(latchPin, GPIO.OUT)
GPIO.setup(clockPin, GPIO.OUT)
GPIO.setup(dataPin, GPIO.OUT)
GPIO.setup(outEnablePin, GPIO.OUT)

def shiftOut( dataByte):
	GPIO.output(clockPin, False)
	GPIO.output(latchPin, False)
	databyte = dataByte
	#GPIO.output(outEnablePin, True)
	for i in range (0,8):
		GPIO.output(clockPin, False)
		GPIO.output(latchPin, False)
		#time.sleep(0.01)
		GPIO.output(dataPin, databyte & 0b1)
		GPIO.output(clockPin, True)
		GPIO.output(latchPin, True)
		databyte = databyte >>1
		#time.sleep(0.01)
		#print databyte
	#GPIO.output(outEnablePin, False)
	#GPIO.output(clockPin, False)
	#GPIO.output(clockPin, True)
	#GPIO.output(clockPin, False)


outs = 0b10101010
for i in range (0,256):
	shiftOut(i)
	#time.sleep(20.0/(i+1))
	GPIO.output(outEnablePin, False)
	time.sleep(1)
	GPIO.output(outEnablePin, True)
	#time.sleep(0.1)
GPIO.output(outEnablePin, False)
shiftOut(outs)
