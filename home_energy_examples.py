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
total_log_aug = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_08/30/2020-10/22/2020"))))
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_11/08/2020-12/25/2020"))))
total_log = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log_12/25/2020-1/14/2021"))))



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
from datetime import timedelta 
from dateutil.relativedelta import relativedelta
from time import sleep
import pickle

eastern = timezone('US/Eastern')

# load the keys from a non repository location
runfile("../keys/ecobee_keys.py")

serv = EcobeeService("Home", application_key,
                     authorization_token=authorization_token,
                     refresh_token=refresh_token)

serv.refresh_tokens()
    
report = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2021, 3, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime.now(), is_dst=True))    
    
eco_log = he.read_ecobee(eco.return_sensor_log(report))

cday = datetime.now()
cday_start = datetime(cday.year, cday.month, cday.day)
cday_int = [cday_start-timedelta(days=2), cday]

total_log_curr = he.add_inst_power(he.createTotalVals(*he.seperateClampVals(he.get_gsheet("SmartThings Log"))))
power_data = he.return_ecobee_data(he.powerdata_to_pd(total_log_curr), cday_int)
eco_test = he.return_ecobee_data(eco_log, cday_int)
he.plot_two_types(eco_test[["Datetime", "Bedroom temperature"]], power_data[["Datetime", "Power (W)"]])
he.plot_ecobee_data(he.return_ecobee_data(eco_log, cday_int))

# day_intervals = [[datetime(2020,12,x,0,0), datetime(2020,12,x,0,0)+timedelta(days=1)] for x in range(1,26)]
# day_intervals = [[datetime(2020,2,x,0,0), datetime(2020,2,x+1,0,0)] for x in range(1,29)]
# day_intervals = [[datetime(2020,3,x,0,0), datetime(2020,3,x+1,0,0)] for x in range(1,30)]

run_time = [he.get_furnace_runtime(he.return_ecobee_data(eco_log, cday=interval)) for interval in day_intervals]
avg_temp = [np.mean(he.return_ecobee_data(eco_log, cday=interval)["outdoorTemp"].values) for interval in day_intervals]


# plots daily usage vs temperature 
# [[cday, he.get_furnace_runtime(he.return_ecobee_data(eco_log_nov, cday=cday)), he.get_avg_temp(eco_log_nov, cday=cday)]for cday in pd.date_range(eco_log_nov["Datetime"][0],eco_log_nov["Datetime"][len(eco_log_nov)-2])]
he.get_runtime_vs_temp(eco_log)

# this backcalculates charging power for the car

power_log = he.powerdata_to_pd(he.return_log(total_log_curr,cday=[datetime(2021,1,8), datetime.now()]))
# power_log = he.powerdata_to_pd(total_log_curr)
ev_charging_grid = he.return_car_charging(power_log, threshold_start=1700, avg_samples=60)
np.sum([ii["Energy (kWh)"] for ii in ev_charging_grid["EventList"]])

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

report_feb = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2019, 2, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2019, 3, 1, 0, 0, 0), is_dst=True))

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

report_dec_cal = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2020, 12, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2020, 12, 31, 23, 59, 0), is_dst=True))    
eco_log_apr = he.read_ecobee(eco.return_sensor_log(report_apr))
eco_log_nov = he.read_ecobee(eco.return_sensor_log(report_nov))
eco_log_dec = he.read_ecobee(eco.return_sensor_log(report_dec))
eco_log_dec_cal = he.read_ecobee(eco.return_sensor_log(report_dec_cal))


# This pulls all data from the server
eco_reports = dict()

eco_reports[11,2019] = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2019, 11, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2019, 11, 30, 23, 59, 0), is_dst=True))

eco_reports[12,2019] = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2019, 12, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2019, 12, 31, 23, 59, 0), is_dst=True))

eco_reports[1,2021] = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2021, 1, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2021, 1, 31, 23, 59, 0), is_dst=True))

eco_reports[2,2021] = eco.get_report_log(serv,\
                            start_date_time=eastern.localize(datetime(2021, 2, 1, 0, 0, 0), is_dst=True),\
                            end_date_time=eastern.localize(datetime(2021, 2, 28, 23, 59, 0), is_dst=True))

    
date_ranges = [[datetime(2020,mm,1), datetime(2020,mm+1,1)  - \
                timedelta(days=1) + timedelta(hours=23, minutes=59)] for mm in range(1,12)]

date_ranges.append([datetime(2020,12,1), datetime(2020,12,31,23,59)])    
for mm in range(1,13):
    eco_reports[mm,2020] =  eco.get_report_log(serv,\
                            start_date_time=eastern.localize(date_ranges[mm-1][0], is_dst=True),\
                            end_date_time=eastern.localize(date_ranges[mm-1][1], is_dst=True))
    sleep(10)
    
# with open('ecobee_reports.pickle', 'wb') as fh:
#     pickle.dump(eco_reports, fh)


with open('data/ecobee_reports.pickle', 'rb') as fh:
    eco_reports = pickle.load(fh)

eco_logs = {kk: he.read_ecobee(eco.return_sensor_log(vv)) for kk,vv in eco_reports.items()}


# Mini split heat capacity estimation
#  Method m2 C = P1 - P0, where m2 is estimated from slope of temperature
# get time when mini split is off before turning on at constant power to maintaining teno
res_down = he.return_ecobee_data(eco_log, [datetime(2021,3,11,4,5), datetime(2021,3,11,5,15)])
res_up = he.return_ecobee_data(eco_log, [datetime(2021,3,11,5,30), datetime(2021,3,11,5,50)])

# units are degrees F / hr
m2 = he.get_slope(eco_log, "Bedroom temperature", [datetime(2021,3,11,4,5), datetime(2021,3,11,5,15)])

m1 = he.get_slope(eco_log, "Bedroom temperature", [datetime(2021,3,11,5,30), datetime(2021,3,11,5,50)])

he.get_slope(eco_log, "Bedroom temperature", [datetime(2021,3,11,4,5), datetime(2021,3,11,5,15)])

# heat capacity of room in kBTU/ degree F
C = 1.3

indoor_steady = he.return_ecobee_data(eco_log, [datetime(2021,3,8,4,35), datetime(2021,3,8,7,50)])
indoor_steady = he.return_ecobee_data(eco_log, [datetime(2021,3,10,5,5), datetime(2021,3,10,7,45)])
np.mean(indoor_steady["Bedroom temperature"]) 
np.mean(indoor_steady["outdoorTemp"]) 
# get power in off state
power_off = he.return_log(total_log_curr, [datetime(2021,3,8,3,35), datetime(2021,3,8,4,5)])


power_on = he.return_log(total_log_curr, cday=[datetime(2021,3,5,4,6), datetime(2021,3,5,8,0)])


minisplit_power = np.mean([x[2] for x in power_on] ) - np.mean([x[2] for x in power_off] )

cop = m2*C / (minisplit_power*3.413e-3)