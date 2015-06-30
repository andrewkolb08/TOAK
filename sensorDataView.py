# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 15:57:39 2015

@author: speechlab
"""

from __future__ import division
from PyQt4 import QtGui, QtCore
import sensor
import sys
import numpy as np


class SensorDataWidget(QtGui.QWidget):
    
    def __init__(self, sensorData=None, parent = None):
        super(SensorDataWidget, self).__init__(parent)
        self.sensorData = sensorData
        self.nameLabel = QtGui.QLabel("<b> Sensor Data </b>")
        rangeLabel = QtGui.QLabel("Range (x,y,z)[mm]: ")
        speedLabel = QtGui.QLabel("Speed [mm/s]: ")
        accelLabel = QtGui.QLabel("Accel [mm/s^2]: ")
        
        layout = QtGui.QGridLayout()
        layout.addWidget(self.nameLabel,0,0,1,3)
        layout.addWidget(rangeLabel,1,0,1,2)
        f = QtGui.QFont("Calibri",7)
        self.ranges = QtGui.QLabel(str(0))
        self.ranges.setFont(f)
        self.speed = QtGui.QLabel(str(0))
        self.speed.setFont(f)
        self.accel = QtGui.QLabel(str(0))
        self.accel.setFont(f)
        layout.addWidget(self.ranges,1,2,1,6)
        layout.addWidget(self.speed,2,2,1,1)
        layout.addWidget(self.accel,3,2,1,1)

        layout.addWidget(speedLabel,2,0,1,2)
        layout.addWidget(accelLabel,3,0,1,2)
        layout.setRowStretch(4,1)
 #       layout.rowStretch(0)
        self.setLayout(layout)
        
    def onFileLoaded(self,sensorData):
        self.sensorData = sensorData
        self.id = sensorData.label
        self.rangeVals = self.sensorData.sensRange()
        self.speedVals = self.sensorData.velocityMag()
        self.accelVals = self.sensorData.accelMag()
        
        self.origVals = (self.rangeVals,self.speedVals,self.accelVals)
        
        self.nameLabel.setText("<b>" + self.sensorData.name + " Data </b>")
        self.ranges.setText(np.array_str(np.around(np.array(self.rangeVals[0],dtype = float),2))+'\n'+np.array_str(np.around(np.array(self.rangeVals[1],dtype = float),2)))
        self.speed.setText(str(self.speedVals[0]))
        self.accel.setText(str(self.accelVals[0]))
        
        
    def updateInterval(self, reset = False):
        if(reset == True):
            self.rangeVals = self.origVals[0]
            self.speedVals = self.origVals[1]
            self.accelVals = self.origVals[2]
        else:
            self.rangeVals = self.sensorData.sensRange()
            self.speedVals = self.sensorData.velocityMag()
            self.accelVals = self.sensorData.accelMag()
        
        self.ranges.setText(np.array_str(np.around(np.array(self.rangeVals[0],dtype = float),2))+'\n'+np.array_str(np.around(np.array(self.rangeVals[1],dtype = float),2)))
        self.speed.setText(str(round(self.speedVals[0],2)))
        self.accel.setText(str(round(self.accelVals[0],2)))
        self.setFixedWidth(self.width())
        
    def updateData(self,index):
        self.speed.setText(str(np.around(np.array(self.speedVals[index],dtype = float),2)))
        self.accel.setText(str(np.around(np.array(self.accelVals[index],dtype = float),2)))


if(__name__ == '__main__'):
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    data = np.genfromtxt(unicode(kinfile), skip_header = 1, delimiter = '\t')
    newSensor = sensor.Sensor(data[:,14:21], None, 'Upper Lip','UL', 400)
    form = SensorDataWidget()
    form.onFileLoaded(newSensor)
    form.updateData(25)
    form.show()
    sys.exit(qtApp.exec_())
