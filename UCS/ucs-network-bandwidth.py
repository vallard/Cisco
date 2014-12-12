#vim: tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab
# (c) vbeninco@cisco.com
# 
# Get Packets (bytes/30seconds) going in and out of blades
# Note:  Please make sure your collection policy is set to collect every 30 seconds.

import getpass
import optparse
import re
from UcsSdk import *
from pprint import pprint
#from pprint_data import data

blades = []
vnics = []


class vnic(object):
	def __init__(self,equipment_name,dn,rx,tx):
		self.equipment_name = equipment_name
		self.dn = dn
		self.rx = rx
		self.tx = tx
		


class blade(object):
	
	def __init__(self,service_profile,equipmentDn):
		self.service_profile = service_profile
		self.equipmentDn = equipmentDn
		self.vnics = []

	def addVnic(self, vnic):
		self.vnics.append(vnic)


def addVnicsToBlades():
	pe = re.compile('/adaptor.*')
	for vnic in vnics:
		# equipment_name: sys/chassis-1/blade-3/adaptor-1/host-eth-4
		# have to remove /adapter...
		vname = pe.sub('',vnic.equipment_name)
		for blade in blades:
			if( vname in blade.equipmentDn):
				blade.addVnic(vnic)
				break


def addVnicStatsToVnic(equipment_name,tx,rx):
	for vnic in vnics:
		# have to strip off the /vnic-stats to make it look like the 
		# equipment name
		ename = equipment_name.replace("/vnic-stats","")
		if(ename == vnic.equipment_name):
			vnic.tx = tx
			vnic.rx = rx
			break	
		

def getServiceProfiles(handle):
	
	crDns = handle.ConfigResolveClass(LsServer.ClassId(), inFilter=None, inHierarchical=YesOrNo.FALSE, dumpXml=None)	
	if(crDns.errorCode == 0):
		for sp in crDns.OutConfigs.GetChild():
			if( sp.AssocState == "associated"):
				blades.append(blade(sp.Dn, sp.PnDn))


def getVnics(handle):
	crDns = handle.ConfigResolveClass(VnicEther.ClassId(), inFilter=None, inHierarchical=YesOrNo.FALSE, dumpXml=None)	
	if(crDns.errorCode == 0):
		SpSet = []
		for v in crDns.OutConfigs.GetChild():
			if v.ConfigState == "applied":
				SpSet.append(v)
				vnics.append(vnic(v.EquipmentDn,v.Dn,0,0))
		return SpSet

def getVhbas(handle):
	crDns = handle.ConfigResolveClass(VnicFc.ClassId(), inFilter=None, inHierarchical=YesOrNo.FALSE, dumpXml=None)	
	if(crDns.errorCode == 0):
		SpSet = []
		for v in crDns.OutConfigs.GetChild():
			if v.ConfigState == "applied":
				SpSet.append(v)
				vnics.append(vnic(v.EquipmentDn,v.Dn,0,0))
		return SpSet

# couldn't figure out how to get this method to work... great documentation... 
def getVints(handle):
	ifs = ClassIdSet()
	f = VnicFc()
	e = VnicEther()
	ifs.AddChild(f)
	ifs.AddChild(e)
	crDns = handle.ConfigResolveClasses(ifs, inHierarchical=YesOrNo.FALSE, dumpXml=None)	
	if(crDns.errorCode == 0):
		SpSet = []
		for v in crDns.OutConfigs.GetChild():
			if v.ConfigState == "applied":
				print v.Dn
				SpSet.append(v)
				vnics.append(vnic(v.EquipmentDn,v.Dn,0,0))
		return SpSet
	else:
		print "error: " + crDns.errorCode
	



def getStats(handle,vnicDns):
	#print vnicDns
	crDns = handle.ConfigResolveDns(vnicDns)
	if(crDns.errorCode == 0):
		for vnic in crDns.OutConfigs.GetChild():
			tx = float(vnic.BytesTxDeltaAvg) * 0.000000254
			rx = float(vnic.BytesRxDeltaAvg) * 0.000000254
			addVnicStatsToVnic(vnic.Dn,tx,rx)
			#print vnic.Dn + ": Tx: " + str(tx) +" Mbps/ Rx: "+ str(rx) + " Mbps"
			print vnic

		#WriteObject(crDns.OutConfigs.GetChild())
	else:
		WriteUcsWarning('[Error]: configResolveDns [Code]:'+crDns.errorCode+ '[Description]:'+crDns.errorDescr)


def doWork(handle):
	#getVints(handle)
	#return
	#sps = getServiceProfilesDns(handle)
	getServiceProfiles(handle)
	vnics = getVnics(handle)
	vhbas = getVhbas(handle)

	# now get vnic stats from all vnics.
	vnicIfs = DnSet()
	for sp in vnics:
		dn = Dn()
		dn.setattr("Value",sp.EquipmentDn + "/vnic-stats")
		vnicIfs.AddChild(dn)
	for sp in vhbas:
		dn = Dn()
		dn.setattr("Value",sp.EquipmentDn + "/vnic-stats")
		vnicIfs.AddChild(dn)
		
	getStats(handle, vnicIfs)

	# finish building the data structure
	addVnicsToBlades()


	# print out blades
	for blade in blades:
		print blade.service_profile
		for v in blade.vnics:
			print "\t{0} tx: {1:.3f} Mbps rx: {2:.3f} Mbps".format(v.dn, v.tx, v.rx)


		


def getpassword(prompt):
	return getpass.unix_getpass(prompt=prompt)


if __name__ == "__main__":
	handle = UcsHandle()
	try: 
		parser = optparse.OptionParser()
		parser.add_option('-i', '--ip',dest="ip", help="[Mandatory] UCSM IP Address")
		parser.add_option('-u', '--username',dest="userName", help="[Mandatory] Account Username for UCSM Login")
		parser.add_option('-p', '--password',dest="password", help="[Mandatory] Account Password for UCSM Login")
		(options, args) = parser.parse_args()
		
		if not options.ip:
			parser.print_help()
			parser.error("Provide UCSM IP address")
		if not options.userName:
			paraser.print_help()
			parser.error("Provide UCSM user name")
		if not options.password:
			options.password=getpassword("UCSM Password:")
		
		handle.Login(options.ip, options.userName, options.password)
		doWork(handle)
		handle.Logout()
	except Exception, err:
		#if handle:
		#	handle.Logout()
		print "Exception:", str(err)
