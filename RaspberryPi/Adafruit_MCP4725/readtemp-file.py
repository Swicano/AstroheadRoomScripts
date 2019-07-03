import os
import glob
import time
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir='/sys/bus/w1/devices/'
#file = glob.glob(base_dir+'3b*9f')[0]+'/w1_slave'
block_file = glob.glob(base_dir+'3b*85')[0]+'/w1_slave'
top_file = glob.glob(base_dir+'3b*7b')[0]+'/w1_slave'


def twos_comp (val, bits):
	if (val &(1 << (bits-1))) !=0:
		val = val-(1 << bits)
	return val

coeffmVperC = [0E0, 0.387481063640E-1, 0.332922278800E-4, 0.206182434040E-6 , -0.21882256846E-8, 0.109968809280E-10, -0.30815758720E-13, 0.454791352900E-16, -0.27512901673E-19]  
coeffCpermV = [0E0, 2.592800E1, -7.602961E-1, 4.637791E-2, -2.165394E-3, 6.048144E-5, -7.293422E-7, 0E0]
def read_temp_raw(file):
	f=open(file,'r')
	lines=f.readlines()
	f.close()
	return lines

def read_temp(file):
	lines = read_temp_raw(file)
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string)/1000.0
		temp_f = temp_c*9.0/5.0+32.0
		return temp_c
def read_temp_fromcode(file):
	lines = read_temp_raw(file)
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw(file)
	cjbytes = lines[0][9:11]+lines[0][6]
	cjtemp = float(twos_comp(int(cjbytes,16),12))/16.0
	hjbytes = lines[0][3:5]+lines[0][0:2]
	hjtemp = float(twos_comp((int(hjbytes,16) >>2) & 0x3fff,14))/4.0
	hjmV = (hjtemp-cjtemp)*.05218
	cjmV = 0.0
	for id, Co in enumerate(coeffmVperC):
		cjmV = cjmV + Co*cjtemp**int(id)
	totmV = cjmV + hjmV
	tottemp = 0
	for id, Co in enumerate(coeffCpermV):
		tottemp = tottemp + Co*totmV**int(id)
	return tottemp


	


if __name__ == "__main__":
	while True:
		f = open('test.txt','a')
		f.write(str(time.time())+', '+ str(read_temp_fromcode(block_file))+', '+ str(read_temp_fromcode(top_file))+'\n')
		f.close()
		print(time.time(),read_temp_fromcode(block_file), read_temp_fromcode(top_file))
		#print(read_temp_fromcode(top_file))
		time.sleep(1)
