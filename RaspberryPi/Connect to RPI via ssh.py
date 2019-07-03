# This is a workaround to find a raspberry pi on a network that had a tendency to randomize its' IP address every now and then, that i did not have admin access to.
from subprocess import call;
from Queue import Queue;
from threading import Thread;

def search_for_MAC(ip_range):
	target_file = "C:\\Users\\Gabriel\\Desktop\\a"+str(ip_range.split('.')[2])+".out"
	call(["nmap","-sn", ip_range , '>'+target_file],shell = True);
	f= open(target_file, 'r');
	read_line2= f.readline();
	read_line1= f.readline();
	read_line= f.readline();
	MACaddress = "74:DA:38:06:5A:7B";
	returnvalue = '';
	while not ('Nmap Done' in read_line or read_line==''):
		read_line2= read_line1;
		read_line1= read_line;
		read_line= f.readline();
		if MACaddress in read_line:
			returnvalue = read_line2.split()[4];
			break;
	f.close();
	call(["DEL", target_file],shell=True)
	return returnvalue;

if __name__ == "__main__":
	IpAddress = '';
	for x in xrange(0+236,256+236):
		#print x, x%256;
		#print '10.138.'+str(x)+'.0/24'
		IpAddress = search_for_MAC('10.138.'+str(x%256)+'.0/24');
		if IpAddress !='':
			call(["C:\\Users\\Gabriel\\Downloads\\putty.exe","-ssh", 'pi@'+str(IpAddress) , "-pw" , 'raspberry' ],shell = True);
			break;
	print IpAddress;
		
	
