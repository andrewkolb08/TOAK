# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 18:21:30 2015

@author: speechlab
"""

from __future__ import division
from PyQt4 import QtCore, QtGui
import sys
import numpy as np
import spec
import qrc_resources

class SpecWidget(QtGui.QWidget):  
    
    def __init__(self,audiofile=None, parent = None): 
        super(SpecWidget, self).__init__(parent)
        
        zoomInButton = self.createButton(':/zoomIn.png',32,24)   
        zoomOutButton = self.createButton(':/zoomOut.png',32,24)
        
        self.specgram = spec.Spec(self,audiofile)
        bandwidthBoxLabel = QtGui.QLabel('Bandwidth: ')
        freqBoxLabel = QtGui.QLabel('Frequency Range: ')
        zoomLabel = QtGui.QLabel('Zoom In/Out: ')
        self.freqRangeBox = QtGui.QDoubleSpinBox()
        self.freqRangeBox.setRange(0.5,self.specgram.fs/2000)
        self.freqRangeBox.setSingleStep(0.5)
        self.freqRangeBox.setSuffix(' kHz')

        self.bandwidthBox = QtGui.QSpinBox()
        self.bandwidthBox.setRange(50, 500)
        self.bandwidthBox.setSingleStep(50)
        self.bandwidthBox.setSuffix(' Hz')
        
        
        self.freqRangeBox.setValue(5000)
        self.bandwidthBox.setValue(300)
        #Add Bandwidth box here.. 
        #Need to adjust bandwidth, wait..., and then update UI
        #See if mpl is faster or my fft is faster
        
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(bandwidthBoxLabel)
        buttonLayout.addWidget(self.bandwidthBox)
        buttonLayout.addWidget(freqBoxLabel)
        buttonLayout.addWidget(self.freqRangeBox)
        buttonLayout.addWidget(zoomLabel)
        buttonLayout.addWidget(zoomInButton)
        buttonLayout.addWidget(zoomOutButton)
        finalLayout = QtGui.QVBoxLayout()
        
        finalLayout.addLayout(buttonLayout)
        finalLayout.addWidget(self.specgram)
        
        self.setLayout(finalLayout)
        
        self.connect(zoomInButton,QtCore.SIGNAL("clicked()"), self.zoomIn)
        self.connect(zoomOutButton,QtCore.SIGNAL("clicked()"), self.zoomOut)
        self.connect(self.freqRangeBox,QtCore.SIGNAL("valueChanged(double)"), self.changeFreqRange) 
        self.connect(self.bandwidthBox,QtCore.SIGNAL("valueChanged(int)"), self.changeBandwidth)
        
        self.setMinimumSize(200,200)
        self.setMaximumHeight(350)
        self.resize(250,300)
        self.zoomList = None
    
        
        if(audiofile is not None):
            self.onFileLoaded(audiofile)
            
        
    def onFileLoaded(self,audiofile):
        self.specgram.onFileLoaded(audiofile)
        self.freqRangeBox.setValue(self.specgram.axes.get_ylim()[1]/1000)
        self.bandwidthBox.setValue(self.specgram.bandwidth)
        self.zoomList = [(0, self.specgram.timeLength)]
        
    def changeFreqRange(self,value):
        newValue = value*1000
        self.specgram.updateAxes(newValue)

    def changeBandwidth(self, value):
        if self.zoomList is not None:
            pos = self.zoomList[-1]
            self.emit(QtCore.SIGNAL("pauseGUI()"))
            self.specgram.updateBandwidth(value, pos)
        else:
            return
            
    def screenshot(self,filename):
        self.specgram.screenshot(filename)

    def zoomIn(self):
        if(self.specgram.linePos1 is None or self.specgram.linePos2 is None):
            return
            
        pos1 = self.specgram.linePos1.get_xdata()
        pos2 = self.specgram.linePos2.get_xdata()
        
        if(type(pos1) is list):
            pos1 = pos1[0]
            pos2 = pos2[0]
            
        if( pos1 == 0 or pos2==0 or 
        pos1 == self.specgram.timeLength or pos2 == self.specgram.timeLength):
            return
            
        self.specgram.showPlotArea(pos1,pos2)
        self.zoomList.append((pos1,pos2))  
        self.emit(QtCore.SIGNAL("newInterval(PyQt_PyObject)"), (pos1,pos2))
        
    def zoomOut(self):
        if len(self.zoomList) == 1 :
            return
            
        self.zoomList.pop(-1)
        pos1 = self.zoomList[-1][0]
        pos2 = self.zoomList[-1][1]
        
        self.specgram.showPlotArea(pos1,pos2)
        self.emit(QtCore.SIGNAL("newInterval(PyQt_PyObject)"), (pos1,pos2))
        
    def updateTimePos(self,xpos):
        self.specgram.updateTimePos(xpos)
        
    def mousePressEvent(self,event):
        focusWidget = QtGui.QApplication.focusWidget()
        if (isinstance(focusWidget, QtGui.QDoubleSpinBox) or isinstance(focusWidget,QtGui.QSpinBox)):
            focusWidget.clearFocus()
        QtGui.QWidget.mousePressEvent(self,event)
        
    def createButton(self,iconFile,buttonSize, iconSize):
        """
            Makes a new button to be used in the audio controller buttons.
            Just a helper method.
        """
        newButton = QtGui.QPushButton()
        newButton.setFixedSize(buttonSize,buttonSize)
        newButton.setIcon(QtGui.QIcon(iconFile))
        newButton.setIconSize(QtCore.QSize(iconSize,iconSize))
        return(newButton)
        
if __name__ == "__main__":

    audiofile = "C:/Data/05_ENGL_F_words6.wav"
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    form = SpecWidget(audiofile)
    form.show()
    sys.exit(qtApp.exec_())