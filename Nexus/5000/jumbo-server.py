from cisco import *            # Cisco library - for CLI etc.,
from datetime import datetime  # for timestamp
from time import sleep         # sleep
from sys import *              # for parsing command line arguments 
from socket import *           # get socket constructor and constants
from string import join        # forthe response
import re

# regular expressions for what I'm looking for.
interface_name = re.compile("^Ethernet(\d{1}/\d{1,2}).*")
rxtx_mode = re.compile(".*?(RX|TX).*")
jumbo_packets = re.compile(".*?(\d+) jumbo packets.*")

# socket stuff to send requests back.
s = socket(AF_INET, SOCK_STREAM)    
hostname = "n5k"
server_host = ""
server_port = 50007            # listen on a non-reserved port number
s.bind((server_host, server_port))  
s.listen(5)                         
s.setblocking(0)                   


def do_jumbo(connection):
	jumbo_command = "show interface"
	output = CLI(jumbo_command, False).get_output() 
	for line in output:
		if interface_name.match(line):
			interface = interface_name.findall(line)[0]
			#print interface
		if rxtx_mode.match(line):
			rxtx = rxtx_mode.findall(line)[0]
			#print rxtx
		if jumbo_packets.match(line):
			jumbo_packets_counter = jumbo_packets.findall(line)[0]
			#print jumbo_packets_counter
			send_info(connection, interface, rxtx, jumbo_packets_counter)

def send_info(conn, interface, rxtx, packets):
	port = "Ethernet " + interface
	msg = (port, rxtx, packets)
	msg = join(msg,sep=' ')
	conn.sendall(msg + "\n")

print "Listening for client requests..."
while 1:                                # listen until process is killed/stopped
    sleep(1)                               # sleep for a second
    try:
        connection, address = s.accept()   # Check for any connection requests
    except :                                      # may fail if no new connections
        #print "Waiting... for client"
        pass                                      # dont break - just continue
    else:
        do_jumbo(connection)
        # shutdown is necessary to close the other side's connection.
        connection.shutdown(SHUT_RDWR)
        connection.close()

