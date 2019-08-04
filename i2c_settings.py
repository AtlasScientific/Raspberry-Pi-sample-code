# the timeout needed to query readings and calibrations
LONG_TIMEOUT = 1.5

# timeout for regular commands
SHORT_TIMEOUT = .5

# the default bus for I2C on the newer Raspberry Pis, 
# certain older boards use bus 0
DEFAULT_BUS = 1

# the default address for the sensor
DEFAULT_ADDRESS = 98


LONG_TIMEOUT_COMMANDS = ("R", "CAL")

SLEEP_COMMANDS = ("SLEEP", )
