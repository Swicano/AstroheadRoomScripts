import socket
import sys
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
	try:
		while True:
			print(read_temp_fromcode(block_file), read_temp_fromcode(top_file))
			#print(read_temp_fromcode(top_file))
			time.sleep(1)
			
			HOST = '' #Symbolic name meaning all available interfaces
			PORT = 8901 #Arbitrary non-priviliged port	

			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			print 'Socket Created'
			
			#Bind socket to local host and port
			try:
				s.bind((HOST, PORT))
			except socket.error, msg:
				print 'Bind failed, Error Code :' + str(msg[0]) +' Message ' + msg[1]
				sys.exit()
			print 'Socket Bind Complete'
			
			#start listening on socket
			s.listen(2)
			print 'Socket now listening'
			tempreply = 0.0
			while True:
				#wait to accept a connection - blocing call
				conn, addr = s.accept()
				#print 'connected with ' + addr[0] +':'+str(addr[1])
				data = conn.recv(1024)
				#print str(data)
				readPIDdata = None 
				with open('writtenPID.txt','r') as f:
					readPIDdata = f.read().split()
				if data == 'tem1':
					try:
						tempreply =  read_temp_fromcode(top_file)
					except:
						tempreply = 0.0
					reply = '%06.2f'% tempreply
				elif data == 'tem2':
					try:
						tempreply =  read_temp_fromcode(block_file)
					except:
						tempreply = 0.0
					reply = '%06.2f'% tempreply
			
				elif data == 'volt':
					while os.stat('writtenvoltage.txt').st_size == 0:
						time.sleep(0.1)
					with open('writtenvoltage.txt', 'r') as f:
						read_data = int(f.read())
					reply = '%06.4f'% (read_data*5.0/4095)
				elif data == 'vol2':
					while os.stat('writtenvoltageX.txt').st_size == 0:
						time.sleep(0.1)
					with open('writtenvoltageX.txt', 'r') as f:
						read_data = int(f.read())
						#print read_data
					reply = '%06.4f'% (read_data*5.0/4095)
				elif data == 'PID1':
					reply = '%06.4f'%(float(readPIDdata[0]))
					#pass 	# will return corrected temp
				elif data == 'PID2':
					reply = '%06.4f'%(float(readPIDdata[1]))
					#pass	# will return CJ Temp
				elif data == 'PID3':
					reply = '%06.4f'%(float(readPIDdata[2]))
					#pass	# will return current SetPoint
				elif data == 'PID4':
					reply = '%06.4f'%(float(readPIDdata[3]))
					#pass	# will return HJ temp
				else:
					reply = 'WHAT??'
				#print reply		
				conn.sendall(reply)
				conn.close()
	except KeyboardInterrupt:
		s.close()


