#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 25 22:54:43 2020

@author: xwang7
"""
import csv
import datetime
import urllib.request
import plotly
import plotly.graph_objs as go
import plotly.io as pio
import numpy as np
from plotly.subplots import make_subplots

def csv2list(fname):
    
    if(isinstance(fname, str)):
        fl = open(fname)
    else:
        fl = fname
    freader = csv.reader(fl)
    lst = []
    for row in freader:
        lst.append(row)
    return lst

def read_solar_log(fname):
    lst = csv2list(fname)
    tdy = datetime.date.today()
    nlst = [[]] * len(lst)
    # dates = [datetime.datetime.strptime(i[0], "%Y-%m-%d %H:%M") for i in lst]
    for i in range(len(lst)):
        nlst[i] = [datetime.datetime.strptime(lst[i][0],"%Y-%m-%d %H:%M"), float(lst[i][1])]
        if(len(lst[i]) > 2):
            nlst[i].append(float(lst[i][2]))                          
    return nlst

def filter_daily_generation_log(sol_log):
    #first filter sol_log so that only the columns that have generation info are returned
    filt_log = [i for i in sol_log if len(i) > 2]
    return filt_log

def add_inst_power(sol_log):
    filt_log = [i for i in sol_log if len(i) > 2]
    nlst = [[]]*(len(filt_log)-1)
    for i in range(1,len(filt_log)):
        nlst[i-1] = [filt_log[i][0], filt_log[i][1], filt_log[i][2], \
                     1000*(filt_log[i][2]-filt_log[i-1][2]) / (((filt_log[i][0]-filt_log[i-1][0]).seconds)/(60*60))]
    return nlst

# def plot_power(pwr, ax = False):
#     if(not(ax)):
#         fig,ax = plt.subplots()       
#     x = [i[0] for i in pwr]
#     y = [i[-1] for i in pwr]
#     fig = plt.gcf()
#     ax.plot_date(x,y,'.-')
#     return fig,ax

# def plot_daily_gen(pwr):
#     daily_gen = daily_generation(pwr)
#     fig,ax = plt.subplots()
#     x = [i[0][0] for i in daily_gen]
#     y = [i[-1] for i in daily_gen]
#     ax.bar(x,y)
#     return fig,ax


#returns the first elements in sol_log matching each day
def return_start_elms(sol_log):
    #returns the first entry of the day
    start_date = sol_log[0][0].replace(hour=0, minute=0)
    end_date = sol_log[-1][0].replace(hour=0, minute=0)
    lst = []
    lst.append(start_date)
    match = []
    while(start_date <= end_date):
        start_date+= datetime.timedelta(days=1)
        lst.append(start_date)
    for cday in lst:
        match.append([]);
        match[-1] = next((i for i in sol_log if i[0].day == cday.day and i[0].month == cday.month), [])
    # filter empty results
    return [i for i in match if i]

def daily_generation(sol_log):
    start_log = return_start_elms(sol_log)
    daily_gen = []
    # daily solar generation will be returned as a date-range, whcih is simply merges the 
    for i in range(1,len(start_log)):
        daily_gen.append([[start_log[i-1][0], start_log[i][0]], start_log[i][2] - start_log[i-1][2]])
    daily_gen.append([[start_log[-1][0], sol_log[-1][0]], sol_log[-1][2] - start_log[-1][2]])
    return daily_gen

#return_log allows filtering of a sol_log (which is returned by read_solar_log)
def return_log(sol_log, cday = datetime.datetime.today()):
    # cday = datetime.date.today();
    if(isinstance(cday, list)):
        return [i for i in sol_log if i[0] >= cday[0] and i[0] <= cday[1] and i[1] > 30]
    else:
        return [i for i in sol_log if i[0].day == cday.day and i[0].month == cday.month and i[1] > 30]        
    

def fetch_log_from_url(url):
    page = urllib.request.urlopen(url)
    return  add_inst_power(read_solar_log(page.read().decode('utf-8').splitlines()))

#this function will write images for the current daily battery voltage, power and accumulated energy
def write_html_log_image(sol_log, fname, cday = datetime.date.today()):
    fig = go.Figure()
    fig2 = go.Figure()
    # fig3 = go.Figure()
    # pio.renderers.default = 'browser'
    day_log = return_log(sol_log,cday)
    xtoday = [i[0] for i in day_log]
    volts = [i[1] for i in day_log]    
    power = [i[-1] for i in day_log]
    energy = [i[-1-1] for i in day_log]
    energy = [i-energy[0] for i in energy]
    # start_day = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    # weekly_gen = daily_generation(return_log(sol_log, [start_day - datetime.timedelta(days=7), datetime.datetime.today()]))
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=xtoday, y = energy, name="Energy (kWh)", mode='lines+markers'), secondary_y=False)
    fig.add_trace(go.Scatter(x=xtoday, y = power, name="Power (W)", mode='lines+markers'), secondary_y=True)
    fig.update_yaxes(title_text="Energy", secondary_y=False)
    fig.update_yaxes(title_text="Power", secondary_y=True)    
    idx = np.array(volts) < 50
    fig2.add_trace(go.Scatter(x=np.array(xtoday)[idx],y = np.array(volts)[idx], name = "Voltage", mode='lines+markers'))
    fig2.update_yaxes(title_text="Voltage")
    # fig3.add_trace(go.Bar(x=[i[0][0] for i in weekly_gen], y = [i[-1] for i in weekly_gen]))
    # fig3.update_yaxes(title_text="Energy")
    with open(fname,'w') as f:
        f.write(fig.to_html(full_html=False, include_plotlyjs='cdn'))
        f.write(fig2.to_html(full_html=False, include_plotlyjs='cdn'))        
        # f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    return fig    

def write_weekly_generation(sol_log, fname):
    
    fig3 = go.Figure()
    start_day = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    time_range = [start_day - datetime.timedelta(days=7), datetime.datetime.today()]
    weekly_gen = daily_generation(return_log(sol_log, time_range))
    write_html_log_image(sol_log,fname,time_range)
    fig3.add_trace(go.Bar(x=[i[0][0] for i in weekly_gen], y = [i[-1] for i in weekly_gen]))
    fig3.update_yaxes(title_text="Energy")
    with open(fname,'a') as f:
        f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    return fig3        