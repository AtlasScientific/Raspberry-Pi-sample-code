#!/usr/bin/python

import io
import sys
import fcntl
import time
import copy
import string
from i2c_settings import (
    DEFAULT_ADDRESS,
    DEFAULT_BUS,
    LONG_TIMEOUT,
    SHORT_TIMEOUT,
    LONG_TIMEOUT_COMMANDS,
    SLEEP_COMMANDS
)


class AtlasI2C:
    def __init__(self, address=None, bus=None):
        '''
        open two file streams, one for reading and one for writing
        the specific I2C channel is selected with bus
        it is usually 1, except for older revisions where its 0
        wb and rb indicate binary read and write
        '''
        self.address = address or DEFAULT_ADDRESS
        self.bus = bus or DEFAULT_BUS
        self._long_timeout = LONG_TIMEOUT
        self._short_timeout = SHORT_TIMEOUT
        self.file_read = io.open(file="/dev/i2c-{}".format(self.bus), 
                                 mode="rb", 
                                 buffering=0)
        self.file_write = io.open(file="/dev/i2c-{}".format(self.bus),
                                  mode="wb", 
                                  buffering=0)
        self.set_i2c_address(self.address)

    @property
    def long_timeout(self):
        return self._long_timeout

    @property
    def short_timeout(self):
        return self._short_timeout

    def set_i2c_address(self, addr):
        '''
        set the I2C communications to the slave specified by the address
        the commands for I2C dev using the ioctl functions are specified in
        the i2c-dev.h file from i2c-tools
        '''
        I2C_SLAVE = 0x703
        fcntl.ioctl(self.file_read, I2C_SLAVE, addr)
        fcntl.ioctl(self.file_write, I2C_SLAVE, addr)
        self.adress = addr

    def write(self, cmd):
        '''
        appends the null character and sends the string over I2C
        '''
        cmd += "\00"
        self.file_write.write(cmd.encode('latin-1'))

    def handle_raspi_glitch(self, response):
        '''
        Change MSB to 0 for all received characters except the first 
        and get a list of characters
        NOTE: having to change the MSB to 0 is a glitch in the raspberry pi, 
        and you shouldn't have to do this!
        '''
        return list(map(lambda x: chr(ord(x) & ~0x80), list()))

    def app_using_python_two(self):
        return sys.version_info[0] < 3

    def get_response(self, raw_data):
        if self.app_using_python_two():
            response = [i for i in raw_data if i != '\x00']
        else:
            response = raw_data

        return response

    def response_valid(self, response):
        valid = True
        error_code = None
        if response[0] != 1:
            if self.app_using_python_two():
                error_code = str(ord(response[0]))
            else:
                error_code = str(response[0])

            valid = False

        return valid, error_code

    def read(self, num_of_bytes=31):
        '''
        reads a specified number of bytes from I2C, then parses and displays the result
        '''
        raw_data = self.file_read.read(num_of_bytes)
        response = self.get_response(raw_data=raw_data)
        is_valid, error_code = self.response_valid(response=response)

        if is_valid:
            char_list = self.handle_raspi_glitch(response[1:])
            result = "Command succeeded " + str(''.join(char_list))
        else:
            result = "Error " + error_code

        return result

    def get_command_timeout(self, command):
        timeout = None
        if command.upper().startswith(LONG_TIMEOUT_COMMANDS):
            timeout = self._long_timeout
        if not command.upper().startswith(SLEEP_COMMANDS):
            timeout = self.short_timeout

        return timeout

    def query(self, command):
        '''
        write a command to the board, wait the correct timeout, 
        and read the response
        '''
        self.write(command)
        current_timeout = self.get_command_timeout(command=command)
        if not current_timeout:
            return "sleep mode"
        else:
            time.sleep(current_timeout)
            return self.read()

    def close(self):
        self.file_read.close()
        self.file_write.close()

    def list_i2c_devices(self):
        '''
        save the current address so we can restore it after
        '''
        prev_addr = copy.deepcopy(self.address)
        i2c_devices = []
        for i in range(0, 128):
            try:
                self.set_i2c_address(i)
                self.read(1)
                i2c_devices.append(i)
            except IOError:
                pass
        # restore the address we were using
        self.set_i2c_address(prev_addr)

        return i2c_devices


def main():
    device = AtlasI2C()
    print('''
        >> Atlas Scientific sample code
        >> Any commands entered are passed to the board via I2C except:
            List_addr lists the available I2C addresses.
            Address,xx changes the I2C address the Raspberry Pi communicates with
            Poll,xx.x command continuously polls the board every xx.x seconds
         where xx.x is longer than the %0.2f second timeout.
        >> Pressing ctrl-c will stop the polling
    ''' % LONG_TIMEOUT)

    real_raw_input = vars(__builtins__).get('raw_input', input)

    while True:
        user_cmd = real_raw_input("Enter command: ")

        if user_cmd.upper().startswith("LIST_ADDR"):
            devices = device.list_i2c_devices()
            for i in range(len(devices)):
                print(devices[i])

        # address command lets you change which address the Raspberry Pi will poll
        elif user_cmd.upper().startswith("ADDRESS"):
            addr = int(user_cmd.split(',')[1])
            device.set_i2c_address(addr)
            print("I2C address set to " + str(addr))

        # continuous polling command automatically polls the board
        elif user_cmd.upper().startswith("POLL"):
            delaytime = float(string.split(user_cmd, ',')[1])

            # check for polling time being too short, change it to the minimum timeout if too short
            if delaytime < AtlasI2C.long_timeout:
                print("Polling time is shorter than timeout, setting polling time to %0.2f" % AtlasI2C.long_timeout)
                delaytime = AtlasI2C.long_timeout

            # get the information of the board you're polling
            info = string.split(device.query("I"), ",")[1]
            print("Polling %s sensor every %0.2f seconds, press ctrl-c to stop polling" % (info, delaytime))

            try:
                while True:
                    print(device.query("R"))
                    time.sleep(delaytime - AtlasI2C.long_timeout)
            except KeyboardInterrupt:       # catches the ctrl-c command, which breaks the loop above
                print("Continuous polling stopped")

        # if not a special keyword, pass commands straight to board
        else:
            if len(user_cmd) == 0:
                print("Please input valid command.")
            else:
                try:
                    print(device.query(user_cmd))
                except IOError:
                    print("Query failed \n - Address may be invalid, use List_addr command to see available addresses")


if __name__ == '__main__':
    main()
