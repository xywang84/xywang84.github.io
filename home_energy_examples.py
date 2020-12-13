#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  1 02:11:30 2020

@author: xwang7
"""
import home_energy as he
# other log file names
gsheet = he.get_gsheet("SmartThings-Log 1/20/2020 - 3/23/2020")
total_log_curr = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log"))))

# fetch from google sheets and return the total log

total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log 3/23/2020 - 4/28/2020"))))
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log 4/28/2020-5/25/2020"))))
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_07/26/2020-08/30/2020"))))
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_08/30/2020-10/22/2020"))))