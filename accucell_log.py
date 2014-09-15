# The MIT License (MIT)
#
# Copyright (c) 2014 Gavin Gallino
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in all
#   copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#   SOFTWARE.
#

# The reference for decoding the data frames comes from the following source
# http://blog.dest-unreach.be/2012/01/29/imax-b6-charger-protocol-reverse-engineered

# for python 2.x pull in the following 3.x features
from __future__ import print_function

import sys, time, serial, argparse

parser = argparse.ArgumentParser(description="Serial data logger for Turnigy Accucell 6 battery charger")
parser.add_argument("port", help="Serial port/path")
parser.add_argument("--debug", action="store_true", help="debug output instead of csv")
parser.add_argument("--verbose", "-v", action="store_true", help="more output columns")
args = parser.parse_args()

try:
  ser = serial.Serial(args.port, baudrate=9600)
except Exception as e:
  print(repr(e), file=sys.stderr)
  sys.exit(1)

mode_names = ['config','li','nimh','nicd','pb','save','load']

# csv columns
csv_simple  = ['timestamp','status', 'voltage', 'current', 'charge_mah']

csv_verbose = csv_simple + ['cell_0_voltage', 'cell_1_voltage', 'cell_2_voltage',
              'cell_3_voltage', 'cell_4_voltage', 'cell_5_voltage', 'checksum',
              'checksum_local', 'cycle_count', 'cycle_mode', 'cycle_mode_chg_dis',
              'cycle_mode_dis_chg', 'input_voltage', 'li_charge_cell_count',
              'li_charge_current', 'li_discharge_cell_count', 'li_discharge_current',
              'mode', 'mode_name', 'nicd_charge_current', 'nicd_discharge_current',
              'nicd_discharge_voltage', 'nimh_charge_current', 'nimh_discharge_current',
              'nimh_discharge_voltage', 'pb_charge_current', 'run', 'state',
              'state_charging', 'state_cycle', 'time_minutes']

# csv headers
if not args.debug and not args.verbose:
  print("#" + ",".join(csv_simple))
elif not args.debug and args.verbose:
  print("#" + ",".join(csv_verbose))

frame = ""

while True:
  try:
    c = ser.read(1)

    if c == '{':
      frame = ""

    elif c == '}' and len(frame) == 74:
      # decode frame
      frame_args = {}
      frame_args['timestamp'] = time.time()
      frame_args['state'] = ord(frame[7]) & 0x7f
      frame_args['state_charging'] = bool(frame_args['state'] & 0x01)
      frame_args['state_cycle'] = bool(frame_args['state'] & 0x10)
      frame_args['nicd_charge_current'] = float(ord(frame[8]) & 0x7f) / 10.0
      frame_args['nicd_discharge_current'] = float(ord(frame[9]) & 0x7f) / 10.0
      frame_args['nimh_charge_current'] = float(ord(frame[12]) & 0x7f) / 10.0
      frame_args['nimh_discharge_current'] = float(ord(frame[13]) & 0x7f) / 10.0
      frame_args['cycle_mode'] = ord(frame[14]) & 0x01
      frame_args['cycle_mode_chg_dis'] = frame_args['cycle_mode'] & 0x01
      frame_args['cycle_mode_dis_chg'] = not frame_args['cycle_mode_chg_dis']
      frame_args['cycle_count'] = ord(frame[15]) & 0x7f
      frame_args['li_charge_current'] = float(ord(frame[16]) & 0x7f) / 10.0
      frame_args['li_charge_cell_count'] = ord(frame[17]) & 0x7f
      frame_args['li_discharge_current'] = float(ord(frame[18]) & 0x7f) / 10.0
      frame_args['li_discharge_cell_count'] = ord(frame[19]) & 0x7f
      frame_args['pb_charge_current'] = float(ord(frame[20]) & 0x7f) / 10.0
      frame_args['mode'] = ord(frame[21]) & 0x7f
      frame_args['run'] = bool(ord(frame[23]) & 1)
      frame_args['nimh_discharge_voltage'] = 0
      frame_args['nicd_discharge_voltage'] = 0
      frame_args['current'] = float(ord(frame[32]) & 0x7f) + (0.01 * float(ord(frame[33]) & 0x7f))
      frame_args['voltage'] = float(ord(frame[34]) & 0x7f) + (0.01 * float(ord(frame[35]) & 0x7f))
      frame_args['input_voltage'] = float(ord(frame[40]) & 0x7f) + (0.01 * float(ord(frame[41]) & 0x7f))
      frame_args['charge_mah'] = (0.1 * float(ord(frame[42]) & 0x7f)) + (0.001 * float(ord(frame[43]) & 0x7f))
      frame_args['cell_0_voltage'] = float(ord(frame[44]) & 0x7f) + (0.01 * float(ord(frame[45]) & 0x7f))
      frame_args['cell_1_voltage'] = float(ord(frame[46]) & 0x7f) + (0.01 * float(ord(frame[47]) & 0x7f))
      frame_args['cell_2_voltage'] = float(ord(frame[48]) & 0x7f) + (0.01 * float(ord(frame[49]) & 0x7f))
      frame_args['cell_3_voltage'] = float(ord(frame[50]) & 0x7f) + (0.01 * float(ord(frame[51]) & 0x7f))
      frame_args['cell_4_voltage'] = float(ord(frame[52]) & 0x7f) + (0.01 * float(ord(frame[53]) & 0x7f))
      frame_args['cell_5_voltage'] = float(ord(frame[54]) & 0x7f) + (0.01 * float(ord(frame[55]) & 0x7f))
      frame_args['time_minutes'] = ord(frame[69]) & 0x7f

      if frame_args['mode'] < len(mode_names):
        frame_args['mode_name'] = mode_names[frame_args['mode']]
      else:
        frame_args['mode_name'] = ''

      if not frame_args['run']:
        frame_args['status'] = "idle"
      elif frame_args['state_charging']:
        frame_args['status'] = "charge"
      else:
        frame_args['status'] = "discharge"

      frame_args['checksum_local'] = sum(map(ord,frame[0:72])) & 0xff
      frame_args['checksum'] = ((ord(frame[72]) & 0xf) << 4) + (ord(frame[73]) & 0xf)

      if args.debug:
        print(repr(frame))
        print(repr(frame_args))
      elif frame_args['checksum_local'] == frame_args['checksum']:
        if args.verbose:
          print(",".join([ str(frame_args[k]) for k in csv_verbose ]))
        else:
          print(",".join([ str(frame_args[k]) for k in csv_simple ]))

      sys.stdout.flush()

      frame = ""

    else:
      frame += c

  except KeyboardInterrupt:
    sys.exit()
  except Exception as e:
    print(repr(e), file=sys.stderr)

