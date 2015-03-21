# -*- coding: utf-8 -*-
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

import sys
import wave
from PyQt4 import QtGui, QtCore
from matplotlib.mlab import specgram
from matplotlib import cm
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
import numpy as np

from scipy.signal import gaussian, lfilter


class Spec(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self,parent = None, audiofile=None, fs=22050, bandwidth=300,freqRange= 5000, dynamicRange=48, noiseFloor =-72):
        self.fig = Figure(figsize=(7,4),dpi = 100)
        self.axes = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)  
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        FigureCanvas.updateGeometry(self)
        
        self.audiofilename = audiofile
        self.freqRange = freqRange
        self.fs = fs
        self.bandwidth = bandwidth
        self.NFFT = self.bw2Nfft(self.bandwidth)
        self.noiseFloor = noiseFloor
        self.dynamicRange = dynamicRange
        self.timeLength = 80
        self.rawSpecData = None
      
        Z=np.zeros((self.timeLength, self.freqRange))
        extent =  0, self.timeLength, 0, self.freqRange
        self.axes.imshow(Z,cm.get_cmap('Greys'), extent = extent, rasterized= True)
#        self.axes.get_xaxis().set_visible(False)        
        self.axes.axis('auto')
#        self.axes.set_xlabel('Time (sec)')
#        self.axes.set_ylabel('Frequency (Hz)')
        self.show()
        
        self.fig.canvas.mpl_connect('button_press_event',self.onclick)
        
        if(self.audiofilename is not None):
            self.onFileLoaded(self.audiofilename)
        
    def onFileLoaded(self,audiofile):   
        self.axes.cla()
        spf = wave.open(audiofile,'r')
        self.signal = spf.readframes(-1)
        self.signal = np.fromstring(self.signal,'Int16')
        self.signal = lfilter([1,-0.97],1,self.signal)
        self.timeLength = len(self.signal)/self.fs
        self.cursor = Cursor(self.axes, horizOn=False)      
        self.linePos1 = None
        self.linePos2 = None
        self.timePos = self.axes.axvline(x = 0,linewidth = 1, color = 'k')
        self.showSignal()        
        self.axes.set_xlabel('Time (sec)')
        self.axes.set_ylabel('Frequency (Hz)')
        self.show()
        

        
    def showSignal(self):
        Pxx, freqs, bins = specgram(self.signal, NFFT = self.NFFT, Fs= self.fs, noverlap = 2*self.NFFT/3, window = gaussian(self.NFFT,self.NFFT/6))
        Z= 10*np.log10(Pxx)
        Z = np.flipud(Z)
        Z[Z>np.amax(Z)-3]= np.amax(Z)-3
        self.rawSpecData = Z
        Z[Z<(np.amax(Z)-self.dynamicRange)]=self.noiseFloor
        extent =  0, self.timeLength, freqs[0], freqs[-1]
        self.axes.imshow(Z,cm.get_cmap('Greys'),extent = extent)
        self.axes.axis('auto')
        self.axes.set_ylim([0,self.freqRange])
        self.axes.set_xlim([0,self.timeLength])
        self.axes.grid(True)
        self.draw()
 #       self.showPlotArea(0,1)
    
    def updateBandwidth(self,bandwidth, pos):
        self.bandwidth = bandwidth
        self.NFFT = self.bw2Nfft(self.bandwidth)
        progress = QtGui.QProgressDialog("Calculating...",QtCore.QString(), 0,100,parent = self)
        progress.setValue(0)
        progress.setMinimumDuration(0)
        progress.forceShow()
        progress.setValue(50)
        self.showSignal()
        self.showPlotArea(pos[0],pos[1])
        self.draw()
        progress.setValue(100)
        progress.destroy()
    
    def screenshot(self,filename):
        self.fig.savefig(filename)
        
    def updateAxes(self,newVal):
        self.freqRange = newVal
        self.axes.set_ylim([0,self.freqRange])
        self.draw()
        
    def showPlotArea(self,time1,time2):
        if(time1 == time2):
            return
        lowBound = min([time1,time2])
        highBound = max([time1,time2])
        self.axes.set_ylim([0,self.freqRange])
        self.axes.set_xlim([lowBound, highBound])
        self.draw()
        
        if(self.linePos1 is not None or self.linePos2 is not None):
            self.linePos1.set_xdata(0)
            self.linePos2.set_xdata(self.timeLength)
        
    def updateCursorPos(self,xpos):
        if(self.linePos1 == None):
            self.linePos1 = self.axes.axvline(x = xpos,linewidth = 1, color = 'r')
        elif(self.linePos2 == None):
            self.linePos2 = self.axes.axvline(x = xpos,linewidth = 1, color = 'r')
        else:
            self.linePos1.set_xdata(self.linePos2.get_xdata())
            self.linePos2.set_xdata(xpos)
        self.draw()
        
    def updateTimePos(self,xpos):
        self.timePos.set_xdata(xpos)
        self.draw()
    
    def onclick(self,event):
        if(event.button == 1):
            self.updateCursorPos(event.xdata)
        elif(event.button == 3):
            self.linePos1.set_xdata(0)
            self.linePos2.set_xdata(self.timeLength)
        
    def bw2Nfft(self,bandwidth):
        toReturn = int(1.2982804/bandwidth*self.fs)
        return toReturn
        
    def nfft2Bw(self,nfft):
        toReturn = int(1.2982804/nfft*self.fs)
        return toReturn
        
if __name__ == '__main__':
    audiofile = "C:/Data/05_ENGL_F_words6.wav"
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    form = Spec()
    form.onFileLoaded(audiofile)
#    form.showPlotArea(2.9,2.7)
#    form.showPlotArea(2.7,2)
#    form.updateCursorPos(2.9)
#    form.updateCursorPos(2.5)
    sys.exit(qtApp.exec_())