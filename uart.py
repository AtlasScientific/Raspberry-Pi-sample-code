#!/usr/bin/python

import serial
import sys
import time
import string 
from serial import SerialException

def read_line():
	"""
	taken from the ftdi library and modified to 
	use the ezo line separator "\r"
	"""
	lsl = len(b'\r')
	line_buffer = []
	while True:
		next_char = ser.read(1)
		if next_char == b'':
			break
		line_buffer.append(next_char)
		if (len(line_buffer) >= lsl and
				line_buffer[-lsl:] == [b'\r']):
			break
	return b''.join(line_buffer)
	
def read_lines():
	"""
	also taken from ftdi lib to work with modified readline function
	"""
	lines = []
	try:
		while True:
			line = read_line()
			if not line:
				break
				ser.flush_input()
			lines.append(line)
		return lines
	
	except SerialException as e:
		print( "Error, ", e)
		return None	

def send_cmd(cmd):
	"""
	Send command to the Atlas Sensor.
	Before sending, add Carriage Return at the end of the command.
	:param cmd:
	:return:
	"""
	buf = cmd + "\r"     	# add carriage return
	try:
		ser.write(buf.encode('utf-8'))
		return True
	except SerialException as e:
		print ("Error, ", e)
		return None
			
if __name__ == "__main__":
	
	real_raw_input = vars(__builtins__).get('raw_input', input) # used to find the correct function for python2/3
	
	print("\nWelcome to the Atlas Scientific Raspberry Pi UART example.\n")
	print("    Any commands entered are passed to the board via UART except:")
	print("    Poll,xx.x command continuously polls the board every xx.x seconds")
	print("    Pressing ctrl-c will stop the polling\n")
	print("    Press enter to receive all data in buffer (for continuous mode) \n")

	# to get a list of ports use the command: 
	# python -m serial.tools.list_ports
	# in the terminal
	usbport = '/dev/ttyAMA0' # change to match your pi's setup 

	print( "Opening serial port now...")

	try:
		ser = serial.Serial(usbport, 9600, timeout=0)
	except serial.SerialException as e:
		print( "Error, ", e)
		sys.exit(0)

	while True:
		input_val = real_raw_input("Enter command: ")

		# continuous polling command automatically polls the board
		if input_val.upper().startswith("POLL"):
			delaytime = float(input_val.split(',')[1])
	
			send_cmd("C,0") # turn off continuous mode
			#clear all previous data
			time.sleep(1)
			ser.flush()
			
			# get the information of the board you're polling
			print("Polling sensor every %0.2f seconds, press ctrl-c to stop polling" % delaytime)
	
			try:
				while True:
					send_cmd("R")
					lines = read_lines()
					for i in range(len(lines)):
						# print lines[i]
						if lines[i][0] != b'*'[0]:
							print( "Response: " + lines[i].decode('utf-8'))
					time.sleep(delaytime)

			except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
				print("Continuous polling stopped")
	
		# if not a special keyword, pass commands straight to board
		else:
			if len(input_val) == 0:
				lines = read_lines()
				for i in range(len(lines)):
					print( lines[i].decode('utf-8'))
			else:
				send_cmd(input_val)
				time.sleep(1.3)
				lines = read_lines()
				for i in range(len(lines)):
					print( lines[i].decode('utf-8'))
