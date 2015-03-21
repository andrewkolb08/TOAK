# -*- coding: utf-8 -*-
"""
Created on Sat Feb 21 15:57:39 2015

@author: speechlab
"""

from __future__ import division
from PyQt4 import QtCore, QtGui
import sensor



class SensorDataWidget(QtGui.QWidget):
    
    def __init__(self, parent = None):
        super(SensorDataWidget, self).__init__(parent)
        


if(__name__ == '__main__'):
    audiofile = "C:/Data/05_ENGL_F_words6.wav"
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    data = np.genfromtxt(unicode(kinfile), skip_header = 1, delimiter = '\t')
    newSensor = sensor.Sensor(data[:,14:21], axes, 'Upper Lip','UL', 400)
    newSensor.accelerationMag()