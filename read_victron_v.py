#!/usr/bin/env python3.5
import serial
import re
import datetime
import pzem
#ser = serial.Serial('/dev/ttyUSB1', 19200)
#s = str(ser.read(153))
#pat_v = "nV\\\\t([0-9]+)"
#m = re.search(pat_v, s)
#orig = m.group(1)
#curr_v = "".join([orig[0:2], ".", orig[2:5]])
curr_v = pzem.read_meter_ac_wrapper(pzem.read_meter_voltage)
curr_v = "{:.2f}".format(curr_v)
datestr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
energy = str(pzem.read_meter_ac_wrapper(pzem.read_meter_energy))
print("".join([datestr, ", ", curr_v, ", ", energy])) 
#print(f"{datestr},{curr_v}, {energy}")
#ser.close()


