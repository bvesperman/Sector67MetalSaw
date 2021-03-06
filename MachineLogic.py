#!/usr/bin/python
import sys
import time 
import datetime 
import RPi.GPIO as io 
import select
import SectorAdminSite
import subprocess
import glob
import os
from pyblinkm import BlinkM, Scripts
import logging 

class MachineLogic:

    rfid =0
    machineID = 11
    isbusy = False
    isOn = False
    SawRelayPin = 24
    IndicatorPin = 23
    lastsawenabledtime= datetime.datetime.now()
    authService = SectorAdminSite.SectorAdmin()
    jobtime = 900
    blinkm = BlinkM()
    LEDStatus = "Off"

    def Busy(self):
        return self.isbusy
    
    def Setup(self):
        io.setmode(io.BCM)
	io.setup(self.SawRelayPin, io.OUT)
	io.output(self.SawRelayPin,False)
	io.setup(self.IndicatorPin, io.OUT)
	io.output(self.IndicatorPin,False)
        self.blinkm.reset()
        #self.blinkm.set_time_adjust(100)
        self.blinkm.go_to(255,0,0)
        #self.blinkm.play_script(Scripts.THUNDERSTORM)
        #self.blinkm.go_to(255,255,255)


    #// If a job has recently ended, report it
    def ReportJob(self):

        newest = max(glob.iglob('/home/pi/ImageLog/*.jpg'), key=os.path.getctime)
        print(newest)
        jpgfile = open(newest).read()
        self.authService.AddMachinePayment(int(self.rfid),self.jobtime,self.machineID, 'Metal Saw Enabled',jpgfile)

    
    def CaptureImage(self):

        subprocess.call("/home/pi/grabPic.sh")


    def CheckBeam(self):
    
        if self.currentstate== "ENABLED":
            if io.input(self.LASERPIN) == 0 and self.laseron == False:
                print("beam on")
                self.laseron = True
                self.laserstarttime = time.localtime()
            elif io.input(self.LASERPIN) == 1 and self.laseron == True:
                self.laseron = False
                print("beam off")
                self.jobtime = ((time.mktime(time.localtime())- time.mktime(self.laserstarttime) -self.JOB_END_TIME))
                if self.jobtime > self.MIN_REPORT_TIME:
                    print("job length of {0} seconds".format(self.jobtime))
                    self.CaptureImage()
                    self.ReportJob()
                self.lastlaserontime = time.localtime()



  

    def DoUnAuthorizedContinuousWork(self):
        if(datetime.datetime.now()-self.lastsawenabledtime).seconds > self.jobtime:
           io.output(self.SawRelayPin, False)
   	   io.output(self.IndicatorPin, False)
	   #print("saw off")
           self.isOn = False
           if(self.LEDStatus <> "Off"):
           	self.blinkm.reset()
           	self.blinkm.go_to(255,0,0)
           	self.LEDStatus = "Off"
        if(datetime.datetime.now()-self.lastsawenabledtime).seconds > self.jobtime - 120 and self.isOn and self.LEDStatus <> "Warning":
           self.blinkm.reset()
           self.blinkm.play_script(Scripts.BLUE_FLASH,40)
           self.LEDStatus = "Warning"

	time.sleep(.25)
        
    def DoAuthorizedWork(self):
	if(self.isOn):
   	   io.output(self.SawRelayPin, False)
   	   io.output(self.IndicatorPin, False)

           if(self.LEDStatus <> "Off"):
           	self.blinkm.reset()
           	self.blinkm.go_to(255,0,0)
                self.LEDStatus = "Off"
 
	   print("saw off")
           logging.exception("saw off")
           self.isOn = False
	else:
	   io.output(self.SawRelayPin,True)
	   io.output(self.SawRelayPin,True)
	   print("saw on")
           logging.exception("saw on")
	   if(self.LEDStatus <> "On"): 
           	self.blinkm.reset()
           	self.blinkm.go_to(0,255,0)
		self.LEDStatus = "On"

           self.isOn = True
           self.lastsawenabledtime= datetime.datetime.now()
           self.ReportJob()



            
