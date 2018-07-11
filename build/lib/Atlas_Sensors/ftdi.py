import string

import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
from pylibftdi import Driver
import os
import time


class AtlasDevice(Device):

	def __init__(self, sn):
		Device.__init__(self, mode='t', device_id=sn)


	def read_line(self, size=0):
		"""
		taken from the ftdi library and modified to 
		use the ezo line separator "\r"
		"""
		lsl = len('\r')
		line_buffer = []
		while True:
			next_char = self.read(1)
			if next_char == '' or (size > 0 and len(line_buffer) > size):
				break
			line_buffer.append(next_char)
			if (len(line_buffer) >= lsl and
					line_buffer[-lsl:] == list('\r')):
				break
		return ''.join(line_buffer)
	
	def read_lines(self):
		"""
		also taken from ftdi lib to work with modified readline function
		"""
		lines = []
		try:
			while True:
				line = self.read_line()
				if not line:
					break
					self.flush_input()
				lines.append(line)
			return lines
		
		except FtdiError:
			print "Failed to read from the sensor."
			return ''		

	def send_cmd(self, cmd):
		"""
		Send command to the Atlas Sensor.
		Before sending, add Carriage Return at the end of the command.
		:param cmd:
		:return:
		"""
		buf = cmd + "\r"     	# add carriage return
		try:
			self.write(buf)
			return True
		except FtdiError:
			print "Failed to send command to the sensor."
			return False
			
			
			
def get_ftdi_device_list():
	"""
	return a list of lines, each a colon-separated
	vendor:product:serial summary of detected devices
	"""
	dev_list = []
	
	for device in Driver().list_devices():
		# list_devices returns bytes rather than strings
		dev_info = map(lambda x: x.decode('latin1'), device)
		# device must always be this triple
		vendor, product, serial = dev_info
		dev_list.append(serial)
	return dev_list


if __name__ == '__main__':

	print "\nWelcome to the Atlas Scientific Raspberry Pi FTDI Serial example.\n"
	print("    Any commands entered are passed to the board via UART except:")
	print("    Poll,xx.x command continuously polls the board every xx.x seconds")
	print("    Pressing ctrl-c will stop the polling\n")
	print("    Press enter to receive all data in buffer (for continuous mode) \n")
	print "Discovered FTDI serial numbers:"

	devices = get_ftdi_device_list()
	cnt_all = len(devices)
	
	#print "\nIndex:\tSerial: "
	for i in range(cnt_all):
		print  "\nIndex: ", i, " Serial: ", devices[i]
	print "==================================="

	index = 0
	while True:
		index = raw_input("Please select a device index: ")

		try:
			dev = AtlasDevice(devices[int(index)])
			break
		except pylibftdi.FtdiError as e:
			print "Error, ", e
			print "Please input a valid index"

	print ""
	print">> Opened device ", devices[int(index)]
	print">> Any commands entered are passed to the board via FTDI:"

	time.sleep(1)
	dev.flush()
	
	while True:
		input_val = raw_input("Enter command: ")

		
		
		# continuous polling command automatically polls the board
		if input_val.upper().startswith("POLL"):
			delaytime = float(string.split(input_val, ',')[1])
			
			dev.send_cmd("C,0") # turn off continuous mode
			#clear all previous data
			time.sleep(1)
			dev.flush()
			
			# get the information of the board you're polling
			print("Polling sensor every %0.2f seconds, press ctrl-c to stop polling" % delaytime)
	
			try:
				while True:
					dev.send_cmd("R")
					lines = dev.read_lines()
					for i in range(len(lines)):
						# print lines[i]
						if lines[i][0] != '*':
							print "Response: " , lines[i]
					time.sleep(delaytime)
	
			except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
				print("Continuous polling stopped")

		else:
			# pass commands straight to board
			if len(input_val) == 0:
				lines = dev.read_lines()
				for i in range(len(lines)):
					print lines[i]
			else:
				dev.send_cmd(input_val)
				time.sleep(1.3)
				lines = dev.read_lines()
				for i in range(len(lines)):
					print lines[i]
