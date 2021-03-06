from cisco import *            # Cisco library - for CLI etc.,
from datetime import datetime  # for timestamp
from time import sleep         # sleep
from sys import *              # for parsing command line arguments 
from socket import *           # get socket constructor and constants
from string import join        # forthe response
import re

# regular expressions for what I'm looking for.
interface_name = re.compile("^Ethernet(\d{1}/\d{1,2}).*")
rx_mode = re.compile(".*?(RX).*")
tx_mode = re.compile(".*?(RX).*")
jumbo_packets = re.compile(".*?(\d+) jumbo packets.*")

# socket stuff to send requests back.
s = socket(AF_INET, SOCK_STREAM)    
# why doesn't the 5k have gethost commend?
hostname = "foohost"
server_host = ""
server_port = 50007            # listen on a non-reserved port number
port = "" # this is global port we are working on
s.bind((server_host, server_port))  
s.listen(5)                         
s.setblocking(0)                   


def do_jumbo(connection):
  jumbo_command = "show interface " + port
  output = CLI(jumbo_command, False).get_output() 
  rx = 0
  tx = 0
  rx_packets = 0
  for line in output:
    if interface_name.match(line):
      interface = interface_name.findall(line)[0]
      #print interface
    if rx_mode.match(line):
      rx = 1
    if rx_mode.match(line):
      tx = 1
    if jumbo_packets.match(line):
      packets = jumbo_packets.findall(line)[0]
      #print jumbo_packets_counter
      if tx:
        send_info(connection, rx_packets, packets)
        tx = 0
        rx = 0
      else:
        rx_packets = packets

def send_info(conn, rx, tx):
  msg = "rx:" + str(rx) + " " + "tx:" + str(tx)
  conn.sendall(msg)

print "Listening for client requests..."
while 1:                                # listen until process is killed/stopped
    sleep(1)                               # sleep for a second
    try:
        connection, address = s.accept()   # Check for any connection requests
    except :                                      # may fail if no new connections
        #print "Waiting... for client"
        pass                                      # dont break - just continue
    else:
        port = connection.recv(1024)
        do_jumbo(connection)
        # shutdown is necessary to close the other side's connection.
        connection.shutdown(SHUT_RDWR)
        connection.close()

