#!/usr/bin/python
import string

import serial
import sys

import time
from serial import SerialException


def read_data():
    line = ""
    try:
        s_time = time.time()
        n = 0
        while True:
            data = ser.read()
            if data == "\r":		# Atlas sensors are sending CR at the end of every response.
                return line
            else:
                line = line + data
            n += 1
            if time.time() - s_time > ser.timeout:
                # print "UART reading timeout."
                return None

    except SerialException as e:
        print "Error, ", e
        return None


if __name__ == "__main__":
    
    print(">> Atlas Scientific Raspberry Pi sample code")
    print(">> Any commands entered are passed to the board via UART except:")
    print(">> Poll,xx.x command continuously polls the board every xx.x seconds")
    print(" Pressing ctrl-c will stop the polling")

    usbport = '/dev/ttyAMA0'

    print "Opening serial port now..."

    try:
        ser = serial.Serial(usbport, 9600, timeout=3)
    except serial.SerialException as e:
        print "Error, ", e
        sys.exit(0)

    while True:
        input_val = raw_input("Enter command: ")

        # continuous polling command automatically polls the board
        if input_val.upper().startswith("POLL"):
            delaytime = float(string.split(input_val, ',')[1])

            # get the information of the board you're polling
            print("Polling sensor every %0.2f seconds, press ctrl-c to stop polling" % delaytime)

            try:
                while True:
                    ser.write("R\r")
                    val = read_data()
                    if val is not None:
                        print "Response: ", val
                    time.sleep(delaytime)

            except KeyboardInterrupt: 		# catches the ctrl-c command, which breaks the loop above
                print("Continuous polling stopped")

        # if not a special keyword, pass commands straight to board
        else:
            if len(input_val) == 0:
                print "Please input valid command."
            else:
                ser.write(input_val + "\r")
                val = read_data()
                if val is not None:
                    print "Response: ", val
