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
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_11/08/2020-12/25/2020"))))


files = glob.glob('data/*.csv')
res = he.read_ecobee(files[1])
# this gets the thermostat data for the time period with insulation
insulate = he.return_ecobee_data(res, [datetime.datetime(2020,12,22,17,00), datetime.datetime(2020,12,23,5,00)])
no_insulate = he.return_ecobee_data(res, [datetime.datetime(2020,12,23,17,00), datetime.datetime(2020,12,24,5,00)])

# rate of heat loss = C * delta(T) 

# get the emp
c1 = he.heat_loss_rate(insulate, 15)
c2 = he.heat_loss_rate(no_insulate,15)

# from pyzt import timezone
from pyecobee import EcobeeService
from datetime import datetime
from pytz import timezone
import xywpyecobee as eco
import csv
eastern = timezone('US/Eastern')

# load the keys from a non repository location
runfile("../keys/ecobee_keys.py")

serv = EcobeeService("Home", application_key,
                     authorization_token=authorization_token,
                     refresh_token=refresh_token)

serv.refresh_tokens()
report_feb = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2020, 2, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2020, 3, 1, 0, 0, 0), is_dst=True))

report_apr = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2020, 3, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2020, 4, 1, 0, 0, 0), is_dst=True))
    

report_nov = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2020, 10, 22, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2020, 11, 18, 0, 0, 0), is_dst=True))        
    
report_dec = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2020, 11, 18, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2020, 12, 18, 0, 0, 0), is_dst=True))    
    
report = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2021, 1, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime.now(), is_dst=True))    
    
eco_log_apr = he.read_ecobee(eco.return_sensor_log(report_apr))
eco_log_nov = he.read_ecobee(eco.return_sensor_log(report_nov))
eco_log_dec = he.read_ecobee(eco.return_sensor_log(report_dec))
eco_log = he.read_ecobee(eco.return_sensor_log(report))

cday = datetime.now()
cday_start = datetime(cday.year, cday.month, cday.day)
cday_int = [cday_start-timedelta(days=1), cday]

total_log_curr = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log"))))
power_data = he.return_ecobee_data(he.powerdata_to_pd(total_log_curr), cday_int)
eco_test = he.return_ecobee_data(eco_log, cday_int)
he.plot_two_types(eco_test[["Datetime", "Bedroom temperature"]], power_data[["Datetime", "Power (W)"]])
he.plot_ecobee_data(he.return_ecobee_data(eco_log, cday_int))

day_intervals = [[datetime(2020,12,x,0,0), datetime(2020,12,x,0,0)+timedelta(days=1)] for x in range(1,26)]
day_intervals = [[datetime(2020,2,x,0,0), datetime(2020,2,x+1,0,0)] for x in range(1,29)]
day_intervals = [[datetime(2020,3,x,0,0), datetime(2020,3,x+1,0,0)] for x in range(1,30)]

run_time = [he.get_furnace_runtime(he.return_ecobee_data(eco_log, cday=interval)) for interval in day_intervals]
avg_temp = [np.mean(he.return_ecobee_data(eco_log, cday=interval)["outdoorTemp"].values) for interval in day_intervals]


# plots daily usage vs temperature 
# [[cday, he.get_furnace_runtime(he.return_ecobee_data(eco_log_nov, cday=cday)), he.get_avg_temp(eco_log_nov, cday=cday)]for cday in pd.date_range(eco_log_nov["Datetime"][0],eco_log_nov["Datetime"][len(eco_log_nov)-2])]
he.get_runtime_vs_temp(eco_log)
# eastern = timezone('US/Eastern')

# selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='', include_alerts=True,
#                       include_device=True, include_electricity=True, include_equipment_status=True,
#                       include_events=True, include_extended_runtime=True, include_house_details=True,
#                       include_location=True, include_management=True, include_notification_settings=True,
#                       include_oem_cfg=False, include_privacy=False, include_program=True, include_reminders=True,
#                       include_runtime=True, include_security_settings=False, include_sensors=True,
#                       include_settings=True, include_technician=True, include_utility=True, include_version=True,
#                       include_weather=True)


# res = serv.request_thermostats(selection)

# report = serv.request_runtime_reports(
#         selection=Selection(
#             selection_type=SelectionType.THERMOSTATS.value,
#             selection_match=res.thermostat_list[0].identifier),
#         start_date_time=eastern.localize(datetime(2020, 12, 24, 0, 0, 0), is_dst=False),
#         end_date_time=eastern.localize(datetime(2020, 12, 25, 0, 0, 0), is_dst=False),
#         include_sensors=True,
#         columns='dmOffset,hvacMode,outdoorHumidity,outdoorTemp,sky,ventilator,wind,zoneAveTemp,'
#                 'zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHumidity,zoneHumidityHigh,'
#                 'zoneHumidityLow,zoneHvacMode,zoneOccupancy')
