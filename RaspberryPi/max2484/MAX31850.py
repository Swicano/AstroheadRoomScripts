import MAX2484

class MAX31850(object):
	'''
	class to use a MAX 31850 digital thermocouple reader via a max2484 i2c to 1wire bridge
	'''
	def __init__(self,address, address_byte_len):
		'''
		initialize the MAX2484 object, and set the address internally
		'''
		self.bridge = MAX2484.MAX2484()
		self.bridge.setSPU(1)
		self.bridge.setAPU(1)
		self.address = address
		self.adlen = address_byte_len
		self.scratchpad = 0
		self.psu = 0
		self.coldjctTemp = 0
		self.hotjctTemp = 0
		
	def twos_comp (self,val, bits):
		if (val &(1 << (bits-1))) !=0:
			val = val-(1 << bits)
		return val
	
	def convertTemp(self):
		self.bridge.use1WDevice(self.address, self.adlen, 0x44, 8, 0)
		
	def readScratchpad(self):
		self.scratchpad = self.bridge.use1WDevice(self.address, self.adlen, 0xBE, 8, 72)
		return self.scratchpad
		
	def readPSU(self):
		self.psu = self.bridge.use1WDevice(self.address, self.adlen, 0xB4, 8, 8)
	
	def readTemp(self):
		coeffmVperC = [0E0, 0.387481063640E-1, 0.332922278800E-4, 0.206182434040E-6 , -0.21882256846E-8, 0.109968809280E-10, -0.30815758720E-13, 0.454791352900E-16, -0.27512901673E-19]  
		coeffCpermV = [0E0, 2.592800E1, -7.602961E-1, 4.637791E-2, -2.165394E-3, 6.048144E-5, -7.293422E-7, 0E0]
		cjtemp = float(self.twos_comp(self.scratchpad >> 20 & 0xFFF,12))/16.0
		self.coldjctTemp = cjtemp
		hjtemp = float(self.twos_comp((self.scratchpad >>2) & 0x3fff,14))/4.0
		hjmV = (hjtemp-cjtemp)*.05218
		cjmV = 0.0
		for id, Co in enumerate(coeffmVperC):
			cjmV = cjmV + Co*cjtemp**int(id)
		totmV = cjmV + hjmV
		tottemp = 0
		for id, Co in enumerate(coeffCpermV):
			tottemp = tottemp + Co*totmV**int(id)
		self.hotjctTemp = tottemp
		return tottemp
		
	