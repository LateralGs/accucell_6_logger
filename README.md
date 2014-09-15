accucell_6_logger
=================

Serial data logger for Turnigy Accucell 6 battery charger and similar models.


Requirements
------------

- Python (tested with 2.7)
- PySerial
  - http://pyserial.sourceforge.net/
- USB to serial adaptor (ftdi or similar)
  - See note below about voltage levels.
- Turnigy Accucell 6 or compatible models
  - [hobbyking product link](http://hobbyking.com/hobbyking/store/__18066__Turnigy_Accucel_6_50W_6A_Balancer_Charger_w_Accessories_US_Warehouse_.html)

Optional Requirements
---------------------

- Matplotlib (for plot_log.py)
   - http://matplotlib.org/

Hardware Notes
--------------

The charger outputs a 5v ttl serial signal on the usb/temp port.  On some older versions there may not be the internal connections for serial output.  On one of my chargers I had to use a resistor to jumper the serial output signal to the center pin on the connector (Reference: http://www.rcgroups.com/forums/showthread.php?t=1046318).  Newer models do not need this modification.

#### Pinout (left to right):
- Vcc 5v
- TTL Serial TX
- GND

Note: this is looking at the end panel with the power connector on the left.

#### Connecting the usb-serial adaptor:

If you use a 3.3v usb serial adaptor you will want to place a resistor in series with the tx line.  A value between 1k and 10k should be fine.

~~~
charger tx -> resistor -> ftdi rx
charger gnd -> ftdi gnd
~~~

#### Configuring the charger:

~~~
USER SET PROGRAM -> USB/TEMP Select -> USB Enable
~~~

Using the program
-----------------

~~~
$ python accucell_log.py --help
usage: accucell_log.py [-h] [--debug] [--verbose] port

Serial data logger for Turnigy Accucell 6 battery charger

positional arguments:
  port           Serial port/path

optional arguments:
  -h, --help     show this help message and exit
  --debug        debug output instead of csv
  --verbose, -v  more output columns
~~~

In default mode the script will output csv data which can be piped to a file.  The verbose flag outputs extra columns of data in adition to the default set.  Debug mode outputs the raw input frames along with the python dictionary holding the csv data.

To exit type control-c in the terminal.

Example (linux):

~~~
$ python accucell_log.py /dev/ttyUSB0 | tee log_file.csv
~~~
