
import time
import logging
import math

import Adafruit_GPIO.FT232H as FT232H
FT232H.use_FT232H();
ft232H = FT232H.FT232H()


class MCP4725(object):
	"""class to represent a MCP4725 12-bit DAC adafruit breakout"""
	#default i2c address 
	MCP4725_I2C_ADDR_DEFAULT     = 0x62
	#Registers
	REG_WRITEDAC = 0x40
	REG_WRITEEEPROM = 0x60

	
	def __init__(self, address=MCP4725_I2C_ADDR_DEFAULT, i2c=None, debug = False, **kwargs):
		"""initialize MCP4725 on the specified address, """
		self._logger = logging.getLogger('MCP4725')
		if i2c == None:
			import Adafruit_GPIO.FT232H as FT232H
			FT232H.use_FT232H()
			ft232h = FT232H.FT232H()
		self._device = FT232H.I2CDevice(ft232h, address, **kwargs)
		self.address = address
		self.debug = debug
	
	
	def setVoltage(self, voltage, persist = False):
		"sets the output voltage to the specified value"
		if (voltage > 4095):
			voltage = 4095
		if (voltage <0):
			voltage = 0
		if(self.debug):
			print "setting voltage to %04d" & voltage
		# Value needs to be left shifted 4 bytes for MCP4725
		bytes = [(voltage >> 4) & 0xFF, (voltage <<4) & 0xFF]
		if (persist):
			self._device.writeList(self.REG_WRITEEEPROM, bytes)
		else:
			self._device.writeList(self.REG_WRITEDAC, bytes)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	