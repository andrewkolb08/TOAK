# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 11:25:26 2015

@author: speechlab
"""
from __future__ import division
import visvis as vv
import numpy as np

class Sensor():    
    colorDict = dict(red =(1,0,0), orange=(1,0.5,0), yellow=(1,1,0),
                green=(0,1,0), blue=(0,0,1), purple=(1,0,1), 
                 black=(0,0,0), cyan=(0,1,1), brown=(0.647059, 0.164706,0.164706),
                 pink=(0.737255,0.560784,0.560784), gray=(0.752941,0.752941,0.752941),
                 gold=(0.8,0.498039,0.196078), turquoise=(0.678431,0.917647,0.917647),
                lime= (0.196078,0.8,0.196078),plum=(0.917649,0.678431,0.917649))
    colorOrder = ('red','orange','yellow','green','blue','purple','black','brown','pink','gray',
                  'gold','turquoise','lime','plum')
    numSensors = 0
    labelOffsets = dict(midsagittal = (-2,2,0), front= (0,2,0), top=(-2,0,0), bottom=(2,0,0))
    
    def __init__(self, kinData, axes, name, label, fs, parent = None):
        
         self.name = name
         self.label = label
         self.labelOffset = Sensor.labelOffsets['midsagittal']
         self.axes = axes
         self.fs = fs
         self.vMags = None
         
         baseVector = vv.Point(0,0,1)
         self.quats = [vv.Quaternion(kinData[i,3],kinData[i,4],kinData[i,5],kinData[i,6]) for i in xrange(kinData.shape[0])]         
         
         self.positions = np.array(kinData[:,0:3])
         self.orientations = [tuple(self.quats[i].rotate_point(baseVector)) for i in xrange(kinData.shape[0])]

         self.cone = vv.solidCone(translation = tuple(self.positions[0]),scaling = (1.5,1.5,1.5),direction = self.orientations[0],axesAdjust = False, axes = self.axes)   
         self.text = vv.Text(self.axes, self.label, self.positions[0,0]+self.labelOffset[0], self.positions[0,1]+self.labelOffset[1], self.positions[0,2]+self.labelOffset[2])
         self.color = Sensor.colorDict[Sensor.colorOrder[Sensor.numSensors]] 
         self.cone.faceColor = self.color
         self.intervalPoints = vv.Pointset(self.positions)

         Sensor.numSensors+=1
         
    def updateInterval(self,lowInd,highInd):
        self.intervalPoints = vv.Pointset(self.positions[lowInd:highInd,:])
         
    def plotIntervalPoints(self,lowInd,highInd):
        self.l= vv.plot(self.intervalPoints, mew=0, mw=0.2 , ms='.', mec = self.color, mc = self.color, axesAdjust = False)
        self.l.alpha = 0.1
        
    def removeIntervalPoints(self):
        self.l.Destroy()
        
    def updateDataAndText(self,index):
        self.cone.translation = tuple(self.positions[index,:])
        self.cone.direction = self.orientations[index]
        self.text.x = self.positions[index,0]+self.labelOffset[0]
        self.text.y = self.positions[index,1]+self.labelOffset[1]
        self.text.z = self.positions[index,2]+self.labelOffset[2]
       
    def updateView(self,view):
        self.labelOffset = Sensor.labelOffsets[view]
        
    def sensRange(self):
        #Give the min/maximum x,y,z values as return.
        #Make it a tuple with 6 values and let the other function figure out
        #What they want.
        mins = np.nanmin(np.array(self.intervalPoints.data),axis=0)
        maxes = np.nanmax(np.array(self.intervalPoints.data),axis=0)
        return (tuple(mins),tuple(maxes))
    
    def velocityMag(self):
        #Give the x,y,z velocity values in an array for each value in the
        #interval.  Use the np.gradient function (with 1/fs as the dx,dy,dz value)
        #Will need to make fs an input parameter to making the sensor so we know it.
        v = np.array(self.intervalPoints.data)
        self.vels = np.gradient(v,1/self.fs)[0]
        self.vMags = np.linalg.norm(self.vels,axis = 1)
        return self.vMags
    
    def peakVelocityMag(self):
        #Get the peak speed from the speed array
        #Just use the max command on that guy
        if(self.vMags == None):
            self.velocityMag()
            
        peakV = max(self.vMags)
        return peakV
    
    def accelMag(self):
        #Use the gradient operator on the velocity array: gradient(m)[0] 
        #Makes the velocity be on the columns instead of rows.
        if(self.vMags == None):
            self.velocityMag()
            
        a = np.gradient(self.vels,1/self.fs)[0]
        self.aMags = np.linalg.norm(a,axis=1)
        return self.aMags
        
    def peakAccelMag(self):
        if(self.vMags == None):
            self.velocityMag()
        
        peakA = max(self.aMags)
        return peakA
        
    @staticmethod
    def resetSensorCount():
        Sensor.numSensors = 0
    
if(__name__ == '__main__'):
    figure = vv.gcf()
    axes = vv.gca()
    audiofile = "C:/Data/05_ENGL_F_words6.wav"
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    data = np.genfromtxt(unicode(kinfile), skip_header = 1, delimiter = '\t')
    newSensor = Sensor(data[:,14:21], axes, 'Upper Lip','UL', 400)
    newSensor.updateDataAndText(1000)
    newSensor.accelerationMag()
    
