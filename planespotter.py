#!/usr/bin/env python

import requests
import json
import time

__author__ = "Raoul Endresl"
__copyright__ = "Copyright 2016"
__license__ = "BSD"
__version__ = "0.1"
__status__ = "Prototype"

"""
planespotter.py

This little app shows me planes approaching my local airport. Based on a geo fencing api lookup fed into slack.

You'll need to get your own slack webhook - https://api.slack.com/incoming-webhooks
You'll also need to define LocalAirport code and the lat/lon of the area to seach for. Keep the rance tight, 
but experiment for what works for you. Mine was set up for the approach path as seen from my back window.

Please play nce with adsbexchange. They are doing it for free!
"""

LocalAirport = "YMML"
latitude =	-37.XXXXX 
longitude =	144.XXXXX
rangeKm =	2


def postToSlack( message ):
	slack_url = "https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXXXXXX"
	
	data = {'text':  message }
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	try:
		r = requests.post(slack_url, data=json.dumps(data), headers=headers)
	except:
		print r

def checkForPlane():

	api_url  = "http://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?"
	api_url += "lat=%s&" % latitude
	api_url += "lng=%s&" % longitude
	api_url += "fDstL=0&"
	api_url += "fDstU=%s" % rangeKm
	
	response = requests.get( api_url )
	
	if response.status_code == 200:
		planes = json.loads(response.content)
		return planes
	if response.status_code >= 500:
		print "[*] ADSB Exchange Busy, trying later. %d" % response.status_code
		time.sleep(600)
		return None
	else:
		print "[*] ADSB Exchange API FAILED! %d" % response.status_code
		exit()
		
	return None

while True:
	planesOverhead = checkForPlane()

	if planesOverhead is not None:
		if planesOverhead['acList'] is not None:
			for plane in planesOverhead['acList']:
				try:
					model = plane['Mdl'].split()
					origin = plane['From'].split()
					firstOpLetter = plane['Op'][0]
					
					if firstOpLetter == "A" or firstOpLetter == "E" or firstOpLetter == "I" or firstOpLetter == "U" or firstOpLetter == "O":
						firstLetterVowel = True
					else:
						firstLetterVowel = False
					
					if origin[0] != LocalAirport:
						del origin[0]
						cleanOrigin = " ".join(origin)
						
						if firstLetterVowel:
							mesg = "An %s %s from %s" % ( plane['Op'], model[1], cleanOrigin )
						else:
							mesg = "A %s %s from %s" % ( plane['Op'], model[1], cleanOrigin )
						
					else:
						dest = plane['To'].split()
						del dest[0]
						cleanDest = " ".join(dest)
						
						
						if firstLetterVowel:
							mesg = "An %s %s left for %s" % ( plane['Op'], model[1], cleanDest )
						else:
							mesg = "A %s %s just left for %s" % ( plane['Op'], model[1], cleanDest )
						
					postToSlack( mesg )
					
				except KeyError:
					print plane['Reg']
					
			time.sleep(60)
			
		time.sleep(15)
