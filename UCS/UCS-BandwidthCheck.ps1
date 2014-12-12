<#
.SYNOPSIS

Retrieves bandwidth from individual blades (both vNICs and vHBAs) and prints out in easily consumable graph.

.DESCRIPTION

The scipt uses UCS PowerTool to query the chassis and grab the statistics.  Then we apply a super cool math
formula to give you the output in mbps.  This can tell you if you if you need to increase links from the 
chassis to the fabric interconnect.  

.EXAMPLE

UCS-BandwidthCheck 10.93.234.241 admin CIsco.123

UCS-BandwidthCheck

Ucs-BandwidthCheck 10.93.234.241 

#>
# vim: tabstop=4:softtabstop=4:shiftwidth=4:noexpandtab
# (c) vbeninco@cisco.com
# 
# Get Packets (bytes/30seconds) going in and out of blades
# Note:  Please make sure your collection policy is set to collect every 30 seconds.
# Get the parameters 
# This is really good
param(	
	#[string]$server = "10.93.234.241",
	#[string]$user = "admin",
	#[string]$pass = "Cisco.123"
	[string] $server,
	[string] $user,
	[string] $pass
)

# make sure we have the Cisco module imported
# TODO check that its not already included.
Import-Module CiscoUCSPS

$slotWidth = 50
# width of our display is the width of two slots plus 6 for the borders
$chassisWidth = ($slotWidth * 2) + 6
$chassisArray = @()


# draw the header of the chassis then call DrawSlots to draw the rest of it.
Function DrawChassis {
	param(
		[hashtable] $bladeHash
	)
	# increase this in case we updated the width of the slots from below.
	$chassisWidth = ($slotWidth * 2) + 6
	
	foreach($ch in $chassisArray) {
		# we only do odd slots because we do in pairs. 
		do {
			Write-Host -NoNewline =
			$i++
		}while($i -lt $chassisWidth)
		$headWidth = $chassisWidth - 4
		Write-Host ""
		$line = "||{0, -$headWidth}||" -f " "
		Write-Host $line
		$line = "||{0, -$headWidth}||" -f "Chassis-$ch"
		Write-Host $line
		$line = "||{0, -$headWidth}||" -f " "
		Write-Host $line
		
		DrawSlots $ch 1 $bladeHash
		DrawSlots $ch 3 $bladeHash
		DrawSlots $ch 5 $bladeHash
		DrawSlots $ch 7 $bladeHash
		# Draw the bottom of the Chassis
		$i = 0
		do {
			Write-Host -NoNewline =
			$i++
		}while($i -lt $chassisWidth)
		Write-Host ""
		Write-Host ""
	}
		
}

Function DrawSlots {
	param(
		[int] $chassis,
		[int] $slot, 
		[hashtable] $bladeHash
	)
	# draw the top of the chassis
	$i = 0
	do {
		Write-Host -NoNewline =
		$i++
	}while($i -lt $chassisWidth)
	# the new line at the end
	Write-Host ""

	# now draw the side
	Write-Host -NoNewline "||"
	$height = 0
	$rvnics = @{}
	$lvnics = @{}
	# Get the blade on the right info
	if ($bladeHash.ContainsKey("sys/chassis-$chassis/blade-$slot")){
		$blade = $bladeHash.Get_Item("sys/chassis-$chassis/blade-$slot")
		if($blade -and $blade.ContainsKey("sp")){
			$sp = $blade.Get_Item("sp")
			$line = "{0, -$slotWidth}" -f $sp
			Write-Host -NoNewline $line
			if($blade.ContainsKey("vnics")){
				$height = $blade.Get_item("vnics").psbase.count + 1
				$rvnics = $blade.Get_item("vnics")
			}
		}
		
	}else {
		$line = "{0, -$slotWidth}" -f " "
		Write-Host -NoNewline $line 	
	}
	# Get the blade on the left info
	Write-Host -NoNewline "||"
	$slot2 = $slot + 1
	if ($bladeHash.ContainsKey("sys/chassis-$chassis/blade-$slot2")){
		$blade = $bladeHash.Get_Item("sys/chassis-$chassis/blade-$slot2")
		if($blade -and $blade.ContainsKey("sp")){
			$sp = $blade.Get_Item("sp")
			$line = "{0, -$slotWidth}" -f $sp	
			Write-Host -NoNewline $line
			if($blade.ContainsKey("vnics")){
				$theight = $blade.Get_item("vnics").psbase.count + 1
				$lvnics = $blade.Get_item("vnics")
				if($theight -gt $height){
					$height = $theight
				}
			}
		}
	}else {
		$line = "{0, -$slotWidth}" -f " "
		Write-Host -NoNewline $line 	
	}

	Write-Host "||"

	# now go through and do the VNICs in the chassis
	$rkeys = @()
	$lkeys = @()
	$rkeys = $rvnics.keys -join ',' -split(',')
	$lkeys = $lvnics.keys -join ',' -split(',')
	$j = 0
	do {
		Write-Host -NoNewline "||"
		# Get the right side
		$line = "{0, -$slotWidth}" -f " "
		if(($rkeys) -and ($j -lt $rkeys.count)){
			$line = "{0, -$slotWidth}" -f $rvnics.Get_item($rkeys[$j])
		}
		Write-Host -NoNewline $line
		Write-Host -NoNewline "||"

		# Get the left side
		$line = "{0, -$slotWidth}" -f " "
		if(($lkeys) -and ($j -lt $lkeys.count)){
			$line = "{0, -$slotWidth}" -f $lvnics.Get_item($lkeys[$j])
		}
		Write-Host -NoNewline $line
		Write-Host "||"

		$j++
	}while($j -lt $height)
	
}


### MAIN Program Begin ##



#Get User parameters
while(!$server){
	$server = Read-Host "Please Enter the UCSM IP address"
}

# Connect to UCSM
# take in the password.  
$handle = ""
if($user -and $pass) {
	$passwd = ConvertTo-SecureString $pass -AsPlainText -Force
	$cred = New-Object System.Management.Automation.PSCredential($user, $passwd)
	Write-Host "Connecting to UCSM... This may take a while to get info."
	$handle = Connect-Ucs $server -Credential $cred
}else {
	# get the password
	Write-Host "Connecting to UCSM... This may take a while to get info."
	$handle = Connect-Ucs $server
}

if(! $handle) {
	Write-Host "Could not connect to UCSM.  Please check parameters"
	exit
}

# We are connected!
# Some commands that we can use in the future to get chassis stuff.  So many places to expand!
#Get-UcsBlade -ChassisId 1 -SlotId 1 | Get-UcsStatistics -Current
#Get-UcsNetworkIfStats  | Get-UcsStatistics -Current
#Get-UcsSwEthLanBorder
#Get-UcsSwFcSanBorder
#Get-UcsUplinkPortChannel
#Get-UcsUplinkPort

# get all the chassis
$chassis = Get-UcsChassis 
foreach($ch in $chassis){
	$chassisArray = $chassisArray +  $ch.Id 
}

# get all the blades in the domain.
$blades = get-UcsBlade
$bladeHash = @{}
# go through each blade.
foreach($blade in $blades) {
	Write-Host "Getting info for blade: "$blade.dn
	if ($blade.association -eq "Associated"){
		$attrsHash = @{}	
		$sp = Get-UcsServiceProfile -Dn $blade.assignedToDn
		#Write-Host "Service Profile: "$sp.dn
		# add SP name to the attribute hash.
		$attrsHash.Add("sp", $sp.rn)
		$vnicHash = @{}
		$vnics = Get-UcsVnic -ServiceProfile $sp
		$vhbas = Get-UCSVhba -ServiceProfile $sp
		foreach($vnic in $vnics){
			$stats = Get-UcsAdaptorVnicStats -Dn ($vnic.equipmentdn + "/vnic-stats")
			$str = "{0}: Tx: {1:N3} Mbps/ Rx: {2:N3} Mbps" -f $vnic.rn, ($stats.BytesTxDeltaAvg * 0.000000254), ($stats.BytesRxDeltaAvg * 0.000000254)
			# check this doesn't get bigger than our width
			if ($str.length -gt $slotWidth){
				$slotWidth = $str.length
			}
			$vnicHash.Add($vnic.rn,$str)
		}
		foreach($vhba in $vhbas){
			$stats = Get-UcsAdaptorVnicStats -Dn ($vhba.equipmentdn + "/vnic-stats")
			$str = "{0}: Tx: {1:N3} Mbps/ Rx: {2:N3} Mbps" -f $vhba.rn, ($stats.BytesTxDeltaAvg * 0.000000254), ($stats.BytesRxDeltaAvg * 0.000000254)
			# check this doesn't get bigger than our width
			if ($str.length -gt $slotWidth){
				$slotWidth = $str.length
			}
			$vnicHash.Add($vhba.rn,$str)
		}
		$attrsHash.Add("vnics", $vnicHash)
		$bladeHash.Add($blade.dn, $attrsHash)
		
	}else {
		$bladeHash.Add($blade.dn, "")
	}

}

DrawChassis $bladeHash
Disconnect-UCS
