#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 27 00:27:06 2020

@author: xwang7
"""


import solar_postprocess as sol

fname = "/home/pi/www/html/cache/victron_log.txt"
vlog = sol.add_inst_power(sol.read_solar_log(fname))
sol.write_weekly_generation(vlog, "/home/pi/www/html/cache/weekly.html")
