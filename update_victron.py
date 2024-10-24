#!/usr/bin/env python3.5
import victron
import time
import pzem
import datetime
import os
fileout = open('/home/pi/www/html/cache/fast_log.html', 'w')
str_start =""" 
<html>
<head>
<meta http-equiv="refresh" content="4">
<title> Current Battery Voltage </title>
</head>
 <h1> """
str_end = "</h1></html>"
count = 0
mcount = 0
while 1:
    fileout.write(str_start)
#    fileout.write(victron.read_victron())
    datestr = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    fileout.write(datestr + " ")
    fileout.write(str(pzem.read_meter_ac_wrapper(pzem.read_meter_voltage)))
    fileout.write("V, ")
    fileout.write(str(pzem.read_meter_ac_wrapper(pzem.read_meter_power)))
    fileout.write("W, ")
    fileout.write(str(pzem.read_meter_ac_wrapper(pzem.read_meter_energy)))
    fileout.write("kWh")
    fileout.write(str_end)
    fileout.seek(0)
    time.sleep(2)
    count = count + 1
"""
    if(count == 30):
        os.system(" ~/www/xywang84.github.io/read_victron_v.py >> ~/www/html/cache/daily_log.txt")
        count = 0
        mcount = mcount+1
    if(mcount == 3):
        os.system("~/www/xywang84.github.io/read_victron_v.py >> ~/www/html/cache/temp_log.txt")
        mcount = 0
"""




