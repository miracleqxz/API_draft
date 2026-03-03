#!/usr/bin/env python

## Tiny Syslog Server in Python.
##
## This is a tiny syslog server that is able to receive UDP based syslog
## entries on a specified port and save them to a file.
## That's it... it does nothing else...
## There are a few configuration parameters.

LOG_FILE = 'youlogfile.log'
HOST, PORT = "0.0.0.0", 5514

#
# NO USER SERVICEABLE PARTS BELOW HERE...
#

import logging
import socketserver
import requests
import json
import re

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filename=LOG_FILE, filemode='a')

ip_cache = {}

class SyslogUDPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]

		ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
		match = re.search(ip_pattern, data)

		if match:
			ip = match.group()
			print("IP:", ip)

			if ip in ip_cache:
				ip_info = ip_cache[ip]
			else:
				try:
					response = requests.get(f'http://ip-api.com/json/{ip}')
					if response.status_code == 200:
						ip_info = response.json()
						ip_cache[ip] = ip_info
					else:
						ip_info = None
				except Exception as e:
					print(f"Error fetching IP info: {e}")
					ip_info = None

			if ip_info:
				data += f" | IP Info: {json.dumps(ip_info)}"

		print("%s : " % self.client_address[0], str(data))
		logging.info(str(data))

if __name__ == "__main__":
	try:
		server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
		server.serve_forever(poll_interval=0.5)
	except (IOError, SystemExit):
		raise
	except KeyboardInterrupt:
		print("Crtl+C Pressed. Shutting down.")