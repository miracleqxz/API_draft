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

class SyslogUDPHandler(socketserver.BaseRequestHandler):

	def handle(self):
		data = bytes.decode(self.request[0].strip())
		socket = self.request[1]

		ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
		match = re.search(ip_pattern, data)

		if match:
			print("IP:", match.group())
			try:
				response = requests.get(f'http://ip-api.com/json/{match.group()}')
				if response.status_code == 200:
					ip_info = response.json()
					data += f" | IP Info: {json.dumps(ip_info)}"
			except Exception as e:
				print(f"Error fetching IP info: {e}")

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