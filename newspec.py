# -*- coding: utf-8 -*-
"""
Created on Sat Feb 14 16:42:39 2015

@author: Andrew
"""

# -*- coding: utf-8 -*-
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

import sys
import wave
from PyQt4 import QtGui, QtCore
import numpy as np
from matplotlib.mlab import specgram
import pyqtgraph as pg

from scipy.signal import gaussian, lfilter
pg.setConfigOption('background','w')
pg.setConfigOption('foreground','k')


class Spec(pg.PlotWidget):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, audiofile=None, fs=22050, bandwidth=300,freqRange= 5000, dynamicRange=48, noiseFloor =-72, parent = None):
        super(Spec, self).__init__()
        
        self.audiofilename = audiofile
        self.freqRange = freqRange
        self.fs = fs
        self.NFFT = int(1.2982804/bandwidth*self.fs)
        self.overlap = int(self.NFFT/2)
        self.noiseFloor = noiseFloor
        self.dynamicRange = dynamicRange
        self.timeLength = 60
        self.resize(700,250)
        
        self.img = pg.ImageItem()
        self.addItem(self.img)
        pos = np.array([0., 1.])
        color = np.array([[255,255,255,255], [0,0,0,255]], dtype=np.ubyte)
        cmap = pg.ColorMap(pos,color)
        lut = cmap.getLookupTable(0.0,1.0,256)
        self.img.setLookupTable(lut)
        
        self.win = gaussian(self.NFFT,self.NFFT/6)
        self.show()
        

#        if(self.audiofilename is not None):
#            self.onFileLoaded(self.audiofilename)
        
    def onFileLoaded(self,audiofile):   
        spf = wave.open(audiofile,'r')
        self.signal = spf.readframes(-1)
        self.signal = np.fromstring(self.signal,'Int16')
        self.signal = lfilter([1,-0.9],1,self.signal)
        self.timeLength = len(self.signal)/self.fs
        self.imgArray = np.empty((1024/2+1,int((len(self.signal)-self.overlap)/(len(self.win)-self.overlap))))
        self.makeFullSpec()
        
        
    def makeFullSpec(self):      
        i = 0
        j=0
        while i < len(self.signal)-self.NFFT:
            zpSignal = np.append(self.win*self.signal[i:i+self.NFFT], np.zeros((1,1024-self.NFFT)))
            spec = np.fft.rfft(zpSignal)/self.NFFT
        
            psd = abs(spec)
            psd = 20*np.log10(psd)

            self.imgArray[:,j]=psd
            j+=1
            i= i+ self.NFFT-self.overlap
            
        freq = np.arange((self.NFFT/2)+1)/(float(self.NFFT)/self.fs)
        yscale = 1.0/(self.imgArray.shape[1]/freq[-1])
        xscale = (1./self.fs)*self.NFFT
        self.img.scale(xscale,yscale)
        self.imgArray[self.img>np.amax(self.imgArray)-3]= np.amax(self.imgArray)-3
        self.imgArray[self.imgArray<(np.amax(self.imgArray)-self.dynamicRange)]=self.noiseFloor
        self.img.setLevels([np.amin(self.imgArray),np.amax(self.imgArray)])
        self.setLabel('left','Frequency', units = 'Hz')
        self.img.setImage(np.transpose(self.imgArray[:,0:15000]),autoLevels=True)
    
                
    def showSignal(self):
        pass
        
    def showPlotArea(self,time,scaling):
        if(time<(0.5/scaling)):
            time = (0.5/scaling)
        elif(time>(self.timeLength-(0.5/scaling))):
            time = self.timeLength - (0.5/scaling)
        
#        self.axes.set_ylim([0,self.freqRange])
#        self.axes.set_xlim([time-(0.5/scaling),time+(0.5/scaling)])
#        self.draw()
        
    def updateCursorPos(self,xpos):
        pass

        
if __name__ == '__main__':
    audiofile = "C:/Data/05_ENGL_F_words6.wav"
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    form = Spec()
    form.show()
    form.onFileLoaded(audiofile)
#    form.showPlotArea(2.7,2)
#    form.updateCursorPos(2.9)
#    form.updateCursorPos(2.5)
    sys.exit(qtApp.exec_())