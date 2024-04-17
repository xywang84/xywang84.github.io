#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 19:13:03 2020

@author: xywang
"""

from pytz import timezone
from pyecobee import Selection,SelectionType
from datetime import datetime
import csv
def get_report_log(serv,start_date_time, end_date_time):
    eastern = timezone('US/Eastern')
    selection = Selection(selection_type=SelectionType.REGISTERED.value, selection_match='', include_alerts=True,
                          include_device=True, include_electricity=True, include_equipment_status=True,
                          include_events=True, include_extended_runtime=True, include_house_details=True,
                          include_location=True, include_management=True, include_notification_settings=True,
                          include_oem_cfg=False, include_privacy=False, include_program=True, include_reminders=True,
                          include_runtime=True, include_security_settings=False, include_sensors=True,
                          include_settings=True, include_technician=True, include_utility=True, include_version=True,
                          include_weather=True)
    
    
    res = serv.request_thermostats(selection)
    
    report = serv.request_runtime_reports(
            selection=Selection(
                selection_type=SelectionType.THERMOSTATS.value,
                selection_match=res.thermostat_list[0].identifier),
            start_date_time=start_date_time,
            end_date_time=end_date_time,
            include_sensors=True,
            columns='dmOffset,hvacMode,outdoorHumidity,outdoorTemp,sky,ventilator,wind,zoneAveTemp,'
                    'zoneCalendarEvent,zoneClimate,zoneCoolTemp,zoneHeatTemp,zoneHumidity,zoneHumidityHigh,'
                    'zoneHumidityLow,zoneHvacMode,zoneOccupancy')
    return report

def return_sensor_log(report):
    sensor_data = report.sensor_list[0]
    header = ["Date,Time" ] + [sensor.sensor_name + " " + sensor.sensor_type for sensor in sensor_data.sensors]        
    data2 = [','.join(entry.split(',')[2:]) for entry in report.report_list[0].row_list] 
    if(len(sensor_data.data) != len(data2)):
        raise Exception("Sensor data is inconsistent length with Report Data")
    return [",".join(header) +"," + report.columns] + [x+','+y for x,y in zip(sensor_data.data,data2)]

def write_csv(report, fname):
    sensor_log = return_sensor_log(report)
    data = "\n".join(sensor_log)
    with open(fname, 'w') as f:
        f.write(data)
    
