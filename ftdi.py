import string

import pylibftdi
from pylibftdi.device import Device
from pylibftdi.driver import FtdiError
import os
import time


class AtlasDevice(Device):

	def read_line(self):
		"""
		Read the response from the Atlas Sensor
		:return:
		"""
		line_buffer = []
		try:
			start_time = time.time()
			while True:

				# read bytes until Carriage Return is received.
				next_char = self.read(1)    # read one byte
				if next_char == "\r":		# response of Atlas sensor is always ended with CR.
					break
				line_buffer.append(next_char)

				if time.time() - start_time > 1.0:  # timeout
					line_buffer = ''
					break
			return ''.join(line_buffer)

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

if __name__ == '__main__':

	print "Welcome to the Atlas Scientific Raspberry Pi example."
	print "Before starting, please get correct serial number by running : python -m pylibftdi.examples.list_devices"

	while True:
		addr = raw_input("Enter Serial Number of device(case sensitive): ")

		try:
			dev = AtlasDevice(addr)
			break
		except pylibftdi.FtdiError as e:
			print "Error, ", e
			print "Please input correct serial number"

	print ""
	print(">> Succeeded to open device")
	print(">> Any commands entered are passed to the board via FTDI except:")
	print(">> SN,xx changes the serial number the Raspberry Pi communicates with.")
	print(">> Poll,xx.x command continuously polls the board every xx.x seconds")
	print(" Pressing ctrl-c will stop the polling")

	while True:
		input_val = raw_input("Enter command: ")

		if input_val.upper().startswith("SN"):
			addr = string.split(input_val, ',')[1]
			dev = AtlasDevice(addr)
			print("FTDI serial number set to " + addr)

		# continuous polling command automatically polls the board
		elif input_val.upper().startswith("POLL"):
			delaytime = float(string.split(input_val, ',')[1])

			print("Polling sensor every %0.2f seconds, press ctrl-c to stop polling" % delaytime)

			try:
				while True:
					dev.send_cmd('R')
					print "Response: ", dev.read_line()
					time.sleep(delaytime)
			except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
				print("Continuous polling stopped")

		# if not a special keyword, pass commands straight to board
		else:
			if len(input_val) == 0:
				print "Please input valid command."
			else:
				dev.send_cmd(input_val)
				print "Response: ", dev.read_line()
