#!/usr/bin/env python
# call: ./jumbo-client-port ip_address port
# example: ./jumbo-client-port 10.1.1.54 e1/1
# example: ./jumbo-client-port 10.1.1.54 po11
# output will be something like: rx:2342 tx:234
import sys
import os
import re
from socket import *

server_host = ''
server_port = 50007

if(len(sys.argv)) > 2:
  server_host = sys.argv[1]
  #print server_host
  port = sys.argv[2]
  #print port
else:
  print "please call this program with an IP address and ethernet port"
  exit()

s = socket(AF_INET, SOCK_STREAM)
try: 
  s.connect((server_host, server_port))
#except Exception, (error, message):
except Exception as e:
  print "Error connecting: check that server is running"
  s.close()
else:
  #print "Got data from server!"
  s.sendall(port)
  while 1:
    data = s.recv(4094)
    if not data: break
    print data
  s.close()
