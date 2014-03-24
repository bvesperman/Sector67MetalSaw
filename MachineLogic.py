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

class MachineLogic:

    rfid =0
    machineID = 5
    isbusy = False
    isOn = False
    SawRelayPin = 24
    IndicatorPin = 23

    #LASERPIN = 25    #// Laser power supply ACTIVE LOW
    #LASERENABLEPIN1 = 23 #// Using two pins to trigger the relay to ensure enough current
    #LASERENABLEPIN2 = 24 #// Using two pins to trigger the relay to ensure enough current
    #JOB_END_TIME = 5 #//Time beam must be off before a job is ended and reported
    #MIN_REPORT_TIME = 5 #//Minimum job length to generate a usage report

    #state = [ "DISABLED",  "VERIFYING",  "ENABLED",  "ENROLLING"]
    #currentstate = "DISABLED"
    #laseron = False
    #laserstarttime = time.localtime()
    #lastlaserontime= time.localtime()
    #jobtime = 0
    authService = SectorAdminSite.SectorAdmin()
    

    def Busy(self):
        return self.isbusy
    
    def Setup(self):

        io.setmode(io.BCM)

	io.setup(self.SawRelayPin, io.OUT)

	io.output(self.SawRelayPin,False)

	io.setup(self.IndicatorPin, io.OUT)

	io.output(self.IndicatorPin,False)



    #// If a job has recently ended, report it
    def ReportJob(self):

        newest = max(glob.iglob('/home/pi/ImageLog/*.jpg'), key=os.path.getctime)
        print(newest)
        jpgfile = open(newest).read()
        self.authService.AddMachinePayment(int(self.rfid),self.jobtime,self.machineID, 'Laser cut time for {0}'.format(self.jobtime),jpgfile)

    
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
   	#if io.input(self.DoorButtonPin) == 1:
	#   io.output(self.SawRelayPin,True)
	#   print("door open")
	time.sleep(.05)
        #   io.output(self.SawRelayPin,False)
        #   print("door closed")
	#self.CheckBeam()
        
    def DoAuthorizedWork(self):
	if(self.isOn):
   	   io.output(self.SawRelayPin, False)
   	   io.output(self.IndicatorPin, False)

	   print("saw off")
           self.isOn = False
	else:
	   io.output(self.SawRelayPin,True)
	   io.output(self.SawRelayPin,True)
	   print("saw on")
           self.isOn = True



            