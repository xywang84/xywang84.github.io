#!/usr/bin/env python3.5
import serial
import re
import datetime
ser = serial.Serial('/dev/ttyUSB1', 19200)
s = str(ser.read(153))
pat_v = "nV\\\\t([0-9]+)"
m = re.search(pat_v, s)
orig = m.group(1)
curr_v = "".join([orig[0:2], ".", orig[2:5]])
datestr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
print("".join([datestr, ", ", curr_v])) 
ser.close()


