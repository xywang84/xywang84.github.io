#!/usr/bin/env python3.5
import minimalmodbus
#from apscheduler.scheduler import Scheduler #Advanced Python Scheduler v2.12
from time import sleep

pz = minimalmodbus.Instrument("/dev/ttyUSB0", 1)
pz.serial.timeout = 0.1 # had to bump this up from the default of 0.05
pz.serial.baudrate = 9600
pz.serial.stopbits = 2
#logging.basicConfig()
#sched = Scheduler()
#sched.start()

def read_meter():
    VOLT = pz.read_register(0, 0, 4)
    AMPS = pz.read_register(1, 0, 4)
    WATT = pz.read_register(2, 0, 4)
    WHRS = pz.read_register(4, 0, 4)
    WHRS_MSB = pz.read_register(5, 0, 4)*2**16
    print(VOLT * 0.01)
    print(AMPS * 0.01)
    print(WATT * 0.1)
    print((WHRS+WHRS_MSB - 32873)/1000)
    print

#returns in KWH
def read_meter_voltage():
    return pz.read_register(0,0,4)*0.01

def read_meter_power():
    return pz.read_register(2, 0, 4)*0.1
def read_meter_energy():
    WHRS = pz.read_register(4, 0, 4)
    WHRS_MSB = pz.read_register(5, 0, 4)*2**16
    CAL_OUT = 32873
    return (WHRS + WHRS_MSB - CAL_OUT)/1000

def read_meter_ac_wrapper(func):
    success = False
    num_tries = 0
    while(success is False and num_tries < 20):
        try:
            result = func()
            success = True
        except:
            sleep(1)
            num_tries = num_tries + 1
    if(num_tries >= 20):
        raise Exception("Num retries exceeded")
    return result

#def main():
#    sched.add_cron_job(read_meter, second='*/1')

#    while True:
#        sleep(1)

#if __name__ == "__main__":
#    main()
