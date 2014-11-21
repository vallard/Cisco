Nexus 5000 Scripts
==================

jumbo scripts:
It turns out the N5k doesn't have an OID for SNMP to get the 
jumbo frame counter packets.  Who knew?  I think its because the
802.1q headers are added to the frames and they count as jumbo frames for
those packets that are full when sent.  

These scripts are used for Cacti.  Its more of a 
proof of concept.  

Server Steps:
* copy the jumbo-server-port.py to your Nexus 5k:
** copy scp://root@10.1.1.100/root/python/jumbo-server-port.py bootflash:/// vrf management
* run the script:
** n5k# python bootflash:///jumbo-server-port.py

This will start a server on the Nexus 5k.  The bad part is that this
has to continue running for the client to work.

Client Steps:
* copy the jumbo-client-port.py to your Cacti host
* Setup Cacti to use it.  (more instructions later)
