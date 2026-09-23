#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 26 23:39:42 2020

@author: xwang7
"""


import solar_postprocess as sol

fname = "/home/pi/www/html/cache/daily_log.txt"
pwr = sol.add_inst_power(sol.read_solar_log(fname))
sol.write_html_log_image(pwr, "/home/pi/www/html/cache/daily.html")

