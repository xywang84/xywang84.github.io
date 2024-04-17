import gspread
from oauth2client.service_account import ServiceAccountCredentials
import numpy as np
import pandas as pd
import datetime 
import plotly
import plotly.graph_objs as go
import plotly.io as pio
from io import StringIO
from plotly.subplots import make_subplots


def open_gsheet(sname):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('../keys/home_energy.json', scope)
    client = gspread.authorize(creds)
    
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    # "SmartThings Log 3/23/2020 - 4/28/2020"
    sheet = client.open(sname).sheet1
    return sheet
    
def get_gsheet(sname):
# use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('../keys/home_energy.json', scope)
    client = gspread.authorize(creds)
    
    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    # "SmartThings Log 3/23/2020 - 4/28/2020"
    sheet = client.open(sname).sheet1
    
    # Extract and print all of the values
    list_of_hashes = sheet.get_all_records()
    df = pd.DataFrame(list_of_hashes)
    try:        
        df["Date/Time"] = df["Date/Time"].transform(lambda x: datetime.datetime.strptime(x, "%m/%d/%Y %H:%M:%S") )
    except:
        df["Date/Time"] = df["Date/Time"].transform(lambda x: datetime.datetime.fromtimestamp(x/1000))
    return df

def process_inverter_log(fname):
    log_base = pd.read_csv(fname)
    new_log = pd.DataFrame({"Date/Time": log_base.iloc[:,0], "Event Value": log_base.iloc[:,1]})
    new_log["Date/Time"] = new_log["Date/Time"].transform(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M") )
    return new_log
    
    
def seperateClampVals(dataframe):
    c1vals = dataframe[dataframe["Device"].str.match("Aeon.*")]
    if(c1vals.empty):
        c1vals = dataframe[dataframe["Device"].str.match(".*Clamp 1")]
        c2vals = dataframe[dataframe["Device"].str.match(".*Clamp 2")]
    else:
        c2vals = None
    return c1vals,c2vals

def createTotalVals(c1vals,c2vals):
    c12vals = dict()
    for index,i in c1vals.iterrows():
        ctime = i["Date/Time"];
        ckey = datetime.datetime(ctime.year, ctime.month, ctime.day, ctime.hour, ctime.minute);        
        # only return first value matching key
        if(not(c12vals.get(ckey, False))):
            c12vals[ckey] = i["Event Value"]        
        lkey = ckey
    # matchKeys = []
    if(c2vals is not None):
        matchKeys = dict()
        for index,i in c2vals.iterrows():
            ctime = i["Date/Time"];
            ckey = datetime.datetime(ctime.year, ctime.month, ctime.day, ctime.hour, ctime.minute);        
            # only return first value matching key, by checking against matchKeys
            if(c12vals.get(ckey, False) and not(matchKeys.get(ckey, False))):
                c12vals[ckey] += i["Event Value"]
                matchKeys[ckey] = True
            lkey = ckey
        combined = dict()
        for i in matchKeys:
            combined[i] = c12vals[i]
        return [[k,v] for k,v in combined.items()]
    else:
        return [[k,v] for k,v in c12vals.items()]

def add_inst_power(sol_log):
    nlst = [[]]*(len(sol_log)-1)
    for i in range(1,len(sol_log)):
        nlst[i-1] = sol_log[i] + \
                     [1000*(sol_log[i][-1]-sol_log[i-1][-1]) / (((sol_log[i][0]-sol_log[i-1][0]).seconds)/(60*60))]
    return nlst

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

def return_end_elms(sol_log):
    #returns the first entry of the day
    start_date = datetime.datetime(sol_log[0][0].year, sol_log[0][0].month,sol_log[0][0].day)
    end_date = datetime.datetime(sol_log[-1][0].year, sol_log[-1][0].month,sol_log[-1][0].day)
    lst = []
    while(start_date <= end_date):        
        lst.append(return_log(sol_log,cday=start_date)[-1])
        start_date+=datetime.timedelta(days=1)
    # filter empty results
    return lst

def daily_generation(sol_log, defaultmode=True):
    start_log = return_start_elms(sol_log)
    daily_gen = []
    # daily solar generation will be returned as a date-range, whcih is simply merges the 
    if(defaultmode):
        for i in range(1,len(start_log)):
            daily_gen.append([[start_log[i-1][0], start_log[i][0]], start_log[i][1] - start_log[i-1][1]])    
        daily_gen.append([[start_log[-1][0], sol_log[-1][0]], sol_log[-1][1] - start_log[-1][1]])
    else:
        for i in range(1,len(start_log)):
            daily_gen.append([[start_log[i-1][0], start_log[i][0]], start_log[i][1]])    
        daily_gen.append([[start_log[-1][0], sol_log[-1][0]], sol_log[-1][1]])
    return daily_gen

def total_consumption(sol_log, fname=False):
    
    fig3 = go.Figure()
    start_day = datetime.datetime.combine(datetime.date.today(), datetime.datetime.min.time())
    # time_range = [sol_log[0][0], sol_log[-1][0]]
    weekly_gen = daily_generation(sol_log)
    fig3.add_trace(go.Bar(x=[i[0][0] for i in weekly_gen], y = [i[-1] for i in weekly_gen]))
    fig3.update_yaxes(title_text="Energy")
    if(fname):
        with open(fname,'w') as f:
            f.write(fig3.to_html(full_html=False, include_plotlyjs='cdn'))
    return fig3        

def plot_consumption(sol_log):
    fig = go.Figure()
    # fig3 = go.Figure()
    pio.renderers.default = 'browser'
    day_log = return_log(sol_log, [sol_log[0][0], sol_log[-1][0]])
    # print([i for i in day_log if abs(i[-1] > 10000)])
    xtoday = [i[0] for i in day_log]
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
    return fig
    # fig3.add_trace(go.Bar(x=[i[0][0] for i in weekly_g

def return_log(sol_log, cday = None):
    if cday is None:
        cday = datetime.datetime.today()
    if(isinstance(cday, list)):
        return [i for i in sol_log if i[0] >= cday[0] and i[0] <= cday[1] and i[-1] > 0 and i[-1] < 20000]
    else:
        return [i for i in sol_log if i[0].day == cday.day and i[0].month == cday.month and i[-1] > 0  and i[-1] < 20000]      

def read_ecobee(ecobee_csv_file, is_from_online=True):
    if(type(ecobee_csv_file) is list):
        is_from_online = False
    if(is_from_online):
        thermDataHeader = pd.read_csv(ecobee_csv_file, skiprows=4).keys()    
        thermDataData = pd.read_csv(ecobee_csv_file, skiprows=6)
        res = {kk:thermDataData.iloc[:,idx] for idx,kk in enumerate(thermDataHeader)}
    else:
        if type(ecobee_csv_file) is str:
            res = pd.read_csv(ecobee_csv_file)
        else:
            res = pd.read_csv(StringIO("\n".join(ecobee_csv_file)))
    res["Datetime"] = (res["Date"]+ " "+res["Time"]).transform(lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S") )
    ecobeeData = pd.DataFrame(res)
    return ecobeeData

def powerdata_to_pd(power_log):
    res = pd.DataFrame(data=power_log, columns=["Datetime","Energy (kWh)","Power (W)"])
    res = res[res["Power (W)"] > 0]
    return res.reset_index()

    
def return_ecobee_data(ecobeeData, cday=None):
    if cday is None:
        cday = datetime.datetime.today()
    if(isinstance(cday, list)):
        idx = ecobeeData["Datetime"].transform(lambda x: x >= cday[0] and x <= cday[1])
    else:
        idx = ecobeeData["Datetime"].transform(lambda x: x.month==cday.month and x.day == cday.day)
    return ecobeeData.loc[idx]


def plot_two_types(y1, y2, xfield="Datetime"):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    name1 = set(y1.keys()) - set([xfield])
    name2 = str(list(set(y2.keys()) - set([xfield]))[0])    
    for nme in name1:
        fig.add_trace(go.Scatter(x=y1[xfield], y=y1[nme], name=nme, mode='lines+markers'), secondary_y = False)
    fig.add_trace(go.Scatter(x=y2[xfield], y=y2[name2], name=name2, mode='lines+markers'), secondary_y = True)
    fig.update_yaxes(title_text="Temperature", secondary_y=False)
    fig.update_yaxes(title_text="Power", secondary_y=True)            
    return fig
def plot_ecobee_data(ecobeeData):
    fig = go.Figure()
    try:
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Current Temp (F)"], name="Main", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Downstairs (F)"], name="Living Room", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Outdoor Temp (F)"], name="Outdoor", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Bedroom (F)"], name="Bedroom", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Sunroom (F)"], name="Sunroom", mode="markers+lines"))
    except:
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Thermostat Temperature temperature"], name="Main", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Downstairs temperature"], name="Living Room", mode="markers+lines"))        
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["outdoorTemp"], name="Outdoor", mode="markers+lines"))     
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Bedroom temperature"], name="Bedroom", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Sunroom temperature"], name="Sunroom", mode="markers+lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["outdoorHumidity"], name="Outdoor Humdity", mode="lines"))
        fig.add_trace(go.Scatter(x=ecobeeData["Datetime"], y=ecobeeData["Thermostat Humidity humidity"], name="Indoor Humdity", mode="lines"))
        
    return fig

def get_furnace_runtime(eco_log):
    """
    Returns the runtime of the ecobee log in minutes

    Parameters
    ----------
    eco_log : pandas array
        DESCRIPTION.

    Returns
    -------
    None.

    """
        
    return len(eco_log["zoneHVACmode"][eco_log["zoneHVACmode"] == "heatStage1On"])*5

def get_avg_temp(eco_log,cday=None):
    if cday is None:
        cday = datetime.datetime.now()
    dat = return_ecobee_data(eco_log, cday=cday)["outdoorTemp"].values    
    return np.mean(dat[np.bitwise_not(np.isnan(dat))])


def get_runtime_vs_temp(eco_log):
    return [[cday, get_furnace_runtime(return_ecobee_data(eco_log, cday=cday)), \
             get_avg_temp(eco_log, cday=cday)]\
            for cday in pd.date_range(eco_log["Datetime"].iloc[0],eco_log["Datetime"].iloc[len(eco_log)-2])]

def running_mean(x, N):
    cumsum = np.cumsum(np.insert(x, 0, 0)) 
    return (cumsum[N:] - cumsum[:-N]) / float(N)

def heat_loss_rate(ecobeeData, navg= 8, room= "Sunroom temperature",get_rate=True):
    delta_t_mins = np.int64(ecobeeData['Datetime'].diff().values)*1e-9/(60)
    # this gives the rate of heat loss in degree F/ min
    try:
        dh_dt = ecobeeData['Sunroom (F)'].diff().values[1:]/delta_t_mins[1:]
        
        
        dTemp = ecobeeData['Outdoor Temp (F)']-ecobeeData['Sunroom (F)']
    except:
        dh_dt = ecobeeData[room].diff().values[1:]/delta_t_mins[1:]
        dTemp = ecobeeData['outdoorTemp']-ecobeeData[room]
    # this gets the sampled rate of heat change    
    if(get_rate):
        c = dh_dt/dTemp.values[1:]
    else:
        c = dh_dt
    c[np.isnan(c)] = 0
    c[np.isinf(c)] = 0
    # print(c)
    return running_mean(c[np.bitwise_not(np.isnan(c))],navg)
    # return(c)

def return_car_charging(power_log, threshold_start=1600, avg_samples = 60, min_run_length=10):
    idx = power_log["Power (W)"] > threshold_start
    temp = power_log["Power (W)"][idx]
    # temp holds all the indicies in power_log that are above the threshold, 
    # we then integrate the consecutive runs. If two indicies aren't part of 
    # the same run, their diff > 1, so disqualify any indicies that didn't
    # maintain an interval. 
    run_lengths = np.cumsum(np.diff(temp.index) == 1)*np.int64(np.diff(temp.index) == 1)
    # need to add a zero at the end to find the most recent instnace
    run_lengths =  np.hstack((run_lengths,0))
    # The start of each run is when 
    run_starts = np.argwhere(run_lengths == 0).flatten()
    intervals = [[run_starts[i]+1, run_starts[i+1]-1] for i in range(len(run_starts)-1)]
    intervals = [v for v in intervals if v[1]-v[0] > min_run_length]
    result = pd.DataFrame()
    # try:
    for intv in intervals:        
        result = result.append(power_log.iloc[temp.index[range(*intv)]])
    idx_locs = [[temp.index[intv[0]], temp.index[intv[1]]+1] for intv in intervals]

    # use avg_samples number of samples to calibrate background
    avg_pwrs = \
        [[(power_log["Energy (kWh)"][ii[0]-1] - power_log["Energy (kWh)"][ii[0]-1-avg_samples])/\
             ((power_log["Datetime"][ii[0]-1] - power_log["Datetime"][ii[0]-1-avg_samples]).seconds/3600), \
          (power_log["Energy (kWh)"][ii[1]+1+avg_samples] - power_log["Energy (kWh)"][ii[1]+1])/ \
              ((power_log["Datetime"][ii[1]+1+avg_samples] - power_log["Datetime"][ii[1]+1]).seconds/3600)] \
                for ii in idx_locs]
    energy_log = power_log["Energy (kWh)"]
    datetime_log = power_log["Datetime"]
    delta_energy = [energy_log[ii[1]] - energy_log[ii[0]] for ii in idx_locs]
    charging_time = [[datetime_log[ii[0]],datetime_log[ii[1]], datetime_log[ii[1]] - datetime_log[ii[0]]] for ii in idx_locs]
    # corrected_energy = [energy_log[ii[1]] - energy_log[ii[0]] - \
    #  np.mean(bg)*(datetime_log[ii[1]] - datetime_log[ii[0]]).seconds/3600 for ii,bg in zip(idx_locs,avg_pwrs)]
    corrected_energy = \
      [energy_log[ii[1]] - energy_log[ii[0]] - \
             np.mean(bg)*(datetime_log[ii[1]] - datetime_log[ii[0]]).seconds/3600 \
      for ii,bg in zip(idx_locs,avg_pwrs)]    
    res_list = [{"Timestamp": tt, "Energy (kWh)": ee, "Raw Energy (kWh)": re, "Corrections (W)": corr}\
                for tt,ee,re,corr in zip(charging_time, corrected_energy, delta_energy, avg_pwrs)]
    out = dict()
    out["DataFrame"] = result
    out["EventList"] = res_list
    return out #,temp,idx_locs, run_lengths, run_starts,intervals
    # except:
    #     return intervals,temp

def get_slope(panda_log, key, interval):
    res = return_ecobee_data(panda_log, interval)
    m = (res[key].iloc[-1] - res[key].iloc[0]) / ((res["Datetime"].iloc[-1]-res["Datetime"].iloc[0]).seconds/3600)
    return m