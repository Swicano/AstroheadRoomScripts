#!/usr/bin/python

import time
import logging
import math

def twos_comp (val, bits):
	if (val &(1 << (bits-1))) !=0:
		val = val-(1 << bits)
	return val

#default i2c address 
MAX2484_I2C_ADDR_DEFAULT     = 0x18

#register addresses
MAX2484_REG_DEV_CONFIG       = 0xC3
MAX2484_REG_STATUS           = 0xF0
MAX2484_REG_READ_DATA        = 0xE1
MAX2484_REG_PORT_CONFIG      = 0xB4

#configuration values for device configuration
DEV_CONFIG_1WS        		 = 0x08
DEV_CONFIG_SPU				 = 0x04
DEV_CONFIG_PDN				 = 0x02
DEV_CONFIG_APU				 = 0x01


#configuration values for port configuration
PORT_CONFIG_1				 = 0x0



import Adafruit_GPIO.FT232H as FT232H
FT232H.use_FT232H();
ft232H = FT232H.FT232H()

class MAX2484(object):
	"""class to represent  a MAX2484 i2c to 1 wire bridge chip """
	
	def __init__(self, address=MAX2484_I2C_ADDR_DEFAULT, i2c=None, **kwargs):
		"""initialize MAX2484 on the specified address, """
		self._logger = logging.getLogger('MAX2484')
		if i2c == None:
			import Adafruit_GPIO.FT232H as FT232H
			FT232H.use_FT232H()
			ft232h = FT232H.FT232H()
		self._device = FT232H.I2CDevice(ft232h, address, **kwargs)
		self.roms = []
		
	def begin(self):
		pass
	
	def deviceReset(self):
		self._device.writeRaw8(0xF0)
	
	def setReadPointer(self, register):
		if register not in (0xC3, 0xF0,0xE1,0xB4):
			self._logger.debug( 'Register not valid, valid registers: 0xC3, 0xF0, 0xE1, 0xB4')
		else:
			self._device.write8(0xE1, register)
	
	def readRegister(self):
		register = self._device.readRaw8()
		return register
	
	def writeDeviceConfig(self, config):
		if (((config >> 4) & 0xF) ^ 0xF) != (config & 0xF):
			self._logger.debug('upper nibble is not one\'s complement of bottom')
		else:
			self._device.write8(0xD2, config)
	
	def adjust1WPort(self, control):
		self._device.write8(0xC3, control)
	
	def reset1W(self):
		self._device.writeRaw8(0xB4)
	
	def singleBit1W(self, byte):
		self._device.write8(0x87, byte)
	
	def writeByte1W(self, byte):
		self._device.write8(0xA5, byte)
	
	def readByte1W(self):
		self._device.writeRaw8(0x96)
	
	def triplet1w(self, byte):
		self._device.write8(0x78, byte)
		
	def setAPU(self, boolAPU):
		self.setReadPointer(MAX2484_REG_DEV_CONFIG)
		currentconfig = self.readRegister()
		new_config_lower= (currentconfig & ~DEV_CONFIG_APU)
		if boolAPU >0:
			new_config_lower =  new_config_lower | DEV_CONFIG_APU
		new_config = (((new_config_lower ^ 0xF) <<4 ) & 0xF0) | (new_config_lower & 0x0F)
		self.writeDeviceConfig(new_config)
		check = self.readRegister()
		if (check & 0x0F) != (new_config & 0x0F):
			self._logger.debug('Device config did not match expected after setAPU')
	
	def setPDN(self, boolPDN):
		self.setReadPointer(MAX2484_REG_DEV_CONFIG)
		currentconfig = self.readRegister()
		new_config_lower= (currentconfig & ~DEV_CONFIG_PDN)
		if boolPDN >0:
			new_config_lower =  new_config_lower | DEV_CONFIG_PDN
		new_config = (((new_config_lower ^ 0xF) <<4 ) & 0xF0) | (new_config_lower & 0x0F)
		self.writeDeviceConfig(new_config)
		check = self.readRegister()
		if (check & 0x0F) != (new_config & 0x0F):
			self._logger.debug('Device config did not match expected after setPDN')
	
	def setSPU(self, boolSPU):
		self.setReadPointer(MAX2484_REG_DEV_CONFIG)
		currentconfig = self.readRegister()
		new_config_lower= (currentconfig & ~DEV_CONFIG_SPU)
		if boolSPU >0:
			new_config_lower =  new_config_lower | DEV_CONFIG_SPU
		new_config = (((new_config_lower ^ 0xF) <<4 ) & 0xF0) | (new_config_lower & 0x0F)
		self.writeDeviceConfig(new_config)
		check = self.readRegister()
		if (check & 0x0F) != (new_config & 0x0F):
			self._logger.debug('Device config did not match expected after setSPU')
		
	def set1WS(self, bool1WS):
		self.setReadPointer(MAX2484_REG_DEV_CONFIG)
		currentconfig = self.readRegister()
		new_config_lower= (currentconfig & ~DEV_CONFIG_1WS)
		if bool1WS >0:
			new_config_lower =  new_config_lower | DEV_CONFIG_1WS
		new_config = (((new_config_lower ^ 0xF) <<4 ) & 0xF0) | (new_config_lower & 0x0F)
		self.writeDeviceConfig(new_config)
		check = self.readRegister()
		if (check & 0x0F) != (new_config & 0x0F):
			self._logger.debug('Device config did not match expected after set1WS')
			
	def ROMsearch(self):
		current_ROM = 0x0
		ROM_list = []
		decision_nodes = []
		first = 1
		while((len(decision_nodes)>0) or (first > 0)):
			#while( first>0):
			first = 0
			self.reset1W()
			self.setReadPointer(0xF0)
			self.writeByte1W(0xF0)
			current_ROM=0x0
			decision_nodes.sort()
			decision_nodes.reverse()
			for i in range(0,64):
				branched = 0
				if len(decision_nodes):
					if (int(i) == int(decision_nodes[0])):
						branched = 1
						self.triplet1w(0x00)
						decision_nodes.pop(0)
					else:
						self.triplet1w(0x80)
				else:
					self.triplet1w(0x80)
				reg = self.readRegister()
				if (reg >>5) == 4:
					if i not in decision_nodes:
						decision_nodes.append(i)
					decision_nodes.sort()
					decision_nodes.reverse()
				current_ROM = ((reg >> 7) << i) | current_ROM
				self._logger.debug(format(current_ROM,'16X'), decision_nodes, i,branched)
			ROM_list.append(current_ROM)
		self.roms = ROM_list
		return self.roms
		
	def checkCRC(self, code, len, crc = 0):
		#load register
		register = code << 8;
		CRC = 0
		XOR = 0
		i=0
		#algorithm is: check bit 0 and bit 9, if they match sends mostly 0's, else send the polynomial
		while i < len:
			bit0 = register & 0x1
			bit9 = (register >>8) & 0x1
			bit = bit0^bit9
			XOR = 0xff &(bit0 << 7 | bit <<2 | bit <<3)
			register = register >>1
			register = register ^ XOR
			i=i+1
			#print(format(register,'8X'))
		return register
		
	def readBytes1W(self, Rxlen):
		bytes = 0
		for i in range(0,Rxlen,8):
			self._device.writeRaw8(0x96) # read a byte from 1W bus, stored in read data register
			self._device.write8(0xE1, 0xE1) # set read pointer to data register
			register = self._device.readRaw8()
			print i
			bytes = ((0xFF & register) << i) | bytes
		return bytes
		
	def use1WDevice(self,address, adlen, TxMsg, Txlen, Rxlen):
		bytes = 0
		self._device.writeRaw8(0xB4) #reset 1W line
		self._device.write8(0xA5, 0x55) #write byte 1W, initiate ROM match
		for i in range(0,adlen, 8): #send address
			self._device.write8(0xA5, address & 0xFF)
			address = address >>8;
		self.setAPU(1)
		for i in range(0,Txlen,8): #send command to 1w device
			self.setSPU(1)
			self._device.write8(0xA5, TxMsg & 0xFF)
			TxMsg = TxMsg >> 8
		for i in range(0,Rxlen,8):
			self.setSPU(1)
			self._device.writeRaw8(0x96) # read a byte from 1W bus, stored in read data register
			self._device.write8(0xE1, 0xE1) # set read pointer to data register
			register = self._device.readRaw8()
			bytes = ((0xFF & register) << i) | bytes
		return bytes
		

			
		
		

if __name__ == '__main__':
	print 'Scanning all I2C bus addresses...'
	for address in range(127):
		if address <= 7 or address >= 120:
			continue
		i2c = FT232H.I2CDevice(ft232H, address)
		if i2c.ping():
			print 'found I2C device at address 0x{0:02X}'.format(address)
	print 'DONE!'