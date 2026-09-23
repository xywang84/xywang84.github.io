#!/usr/bin/env python3.5
import victron
import time
fileout = open('/home/pi/www/html/cache/fast_log.html', 'w')
str_start =""" 
<html>
<head>
<meta http-equiv="refresh" content="4">
<title> Current Battery Voltage </title>
</head>
 <h1> """
str_end = "</h1></html>"
while 1:
    fileout.write(str_start)
    fileout.write(victron.read_victron())
    fileout.write(str_end)
    fileout.seek(0)
    time.sleep(2)

