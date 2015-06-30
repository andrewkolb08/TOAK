# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 12:09:12 2015

@author: Andrew Kolb
"""
from __future__ import division
from PyQt4 import QtCore, QtGui, QtMultimedia
import sys
import lcdTimer as lcd
import numpy as np
import visvis as vv
import sensor
import wave
import os
import specWidget
import qrc_resources
import sensorDataView as sdv


class DataController(QtGui.QWidget):    
    def __init__(self, kinfile, audiofile, config, parent = None):
        """
        Data Controller class receives a kinematic file, and an audiofile, and
        sets them up to be played synchronously using the visvis Figure().  
        
        The LCDTimer is passed the time and updated regularly to display the current
        time values that are playing in the audio and in the kinematic data.  
        The data controls are setup on top with the LCD timer, with the figure below.
        The dataController supports switching views, stopping, pausing, rewinding,
        fast forwarding, playing, etc.  It's purdy neat.
        """
        super(DataController, self).__init__(parent)
        backend = 'pyqt4'
        app = vv.use(backend)
        self.fileLoaded = False
        #Set up the buttons for the player
        self.playPauseButton = self.createButton(':/play.svg',50,44)
        self.stopButton = self.createButton(':/stop.svg',40,34)
        self.ffButton = self.createButton(":/fastForward.svg",30,24)
        self.stepForwardButton = self.createButton(":/skipForward.svg",40,34)
        self.stepBackwardButton = self.createButton(":/skipBackward.svg",40,34)
        self.rewindButton = self.createButton(":/rewind.svg",30,24)
        
        self.config= config
        self.fs = self.config[0]
        self.numSensors = self.config[1]
        self.sensorDataFormat = [(14+9*i,21+9*i, self.config[2][i], self.config[3][i]) for i in range(self.numSensors)]
        print self.sensorDataFormat
        
        Figure = app.GetFigureClass()
        self.setMinimumSize(750,700)
        self.resize(750,700)
        self.fig= Figure(self)
        self.fig.enableUserInteraction = False
        self.fig._widget.setMinimumSize(400,280)
        self.spectrogram = specWidget.SpecWidget()
        self.spectrogram.setMinimumSize(400, 150)
        
        self.lcdTimer = lcd.LcdTimer()
        self.lcdTimer.setMaximumHeight(60)
        self.lcdTimer.setMinimumWidth(100)
        
        self.dataViewers = [sdv.SensorDataWidget() for i in xrange(self.numSensors)];
        
        playerLayout = QtGui.QHBoxLayout()
        playerLayout.addStretch()
        playerLayout.addWidget(self.rewindButton)
        playerLayout.addWidget(self.stepBackwardButton)
        playerLayout.addWidget(self.playPauseButton)
        playerLayout.addWidget(self.stopButton)
        playerLayout.addWidget(self.stepForwardButton)
        playerLayout.addWidget(self.ffButton)
        playerLayout.addWidget(self.lcdTimer)
        
        playerGroup = QtGui.QGroupBox("Data Controls")
        playerGroup.setLayout(playerLayout)
        playerGroup.setMaximumHeight(100)
        
        centerLayout= QtGui.QVBoxLayout()
        centerLayout.addWidget(playerGroup)
        centerLayout.addWidget(self.fig._widget)
        centerLayout.addWidget(self.spectrogram)
        
        finalLayout = QtGui.QHBoxLayout()
        finalLayout.addLayout(centerLayout)
        dataLayout = QtGui.QVBoxLayout()
        
        for DV in self.dataViewers:
            dataLayout.addWidget(DV)
        
        finalLayout.addLayout(dataLayout)
        self.setLayout(finalLayout)
        
        self.connect(self.playPauseButton,QtCore.SIGNAL("clicked()"),self.playPause)
        self.connect(self.stopButton,QtCore.SIGNAL("clicked()"),self.stop) 
        self.connect(self.ffButton,QtCore.SIGNAL("pressed()"),self.fastForward)
        self.connect(self.rewindButton, QtCore.SIGNAL("pressed()"),self.rewind)
        self.connect(self.stepForwardButton,QtCore.SIGNAL("pressed()"),self.stepForward)
        self.connect(self.stepBackwardButton,QtCore.SIGNAL("pressed()"),self.stepBackward)
        self.connect(self.spectrogram,QtCore.SIGNAL("pauseGUI()"),self.stepBackward)      
        self.connect(self.spectrogram,QtCore.SIGNAL("newInterval(PyQt_PyObject)"), self.setNewInterval)
        
        self.playing,self.paused,self.stopped = range(3)
        self.status = self.stopped
        self.timer = vv.Timer(self)
        self.timer.Bind(self.onTimer)
        self.timer.nolag = True
        self.disableButtons()
        if((kinfile is not None) and (audiofile is  not None)):
            self.onFileLoaded(kinfile,audiofile)            
        
        
    def onFileLoaded(self,kinfile,audiofile):  
        """
            Called when the file is loaded or passed into the dataController
            It opens a progress dialog while the files are loaded.
            the axes are set up, the starting row is determined, and the start
            time is shown as well.  The audio file parameters are extracted and
            configured in setupAudioFile()
            
            At the end, we destroy the progress dialog and enable the buttons again.
        """
        self.disableButtons()        
        progress = QtGui.QProgressDialog("Opening File...",QtCore.QString(), 0,100,parent = self)
        progress.setValue(0)
        progress.setMinimumDuration(0)
        progress.forceShow()
        
        sensor.Sensor.resetSensorCount()
        
        self.kinfilename = unicode(kinfile)
        self.audiofilename = unicode(audiofile)
        
        progress.setValue(25)
        self.datavals = self.loadTsv(self.kinfilename)
        
        progress.setValue(50)
        progress.setValue(75)
        self.startRow = self.getStartRow()
        self.timeLength = self.datavals[-1,0]
        self.lcdTimer.showTime(self.datavals[self.startRow,0],self.timeLength)
        self.index = self.startRow
        self.setupAxes()
        self.setInitialSensorDisplay()
        progress.setValue(90)
        self.setupAudioFile()
        self.audioStartOffset = self._headerSize+(int(self.datavals[self.startRow,0]*self._fps) & (-2)) #Get the nearest even packet
        self.kinInterval = (self.startRow,len(self.datavals[:,0])-1)
        self.audioInterval = (self.audioStartOffset, self._headerSize+(int(self.datavals[self.kinInterval[1],0]*self._fps) & (-2)))
        self.spectrogram.onFileLoaded(self.audiofilename)
        
        for DV,sensors in zip(self.dataViewers,self.allSensors):
            DV.onFileLoaded(sensors)

        self.showMidsagittalView()
        self.show()
        progress.setValue(100)
        progress.destroy()
        self.fileLoaded = True
        self.trajectoryMode = False
        self.subjectView = 'midsagittal'
        self.enableButtons()
        
    def getStartRow(self):
        """
            Determines the actual start row of the file..
            The files from the NDI wave typically suck in that they don't start
            at zero and they contain some nonsense timestamps in the beginning
            while the Wave is getting setup.  This file finds the first real 
            timestamp (not 123439 or something), and returns it to be the starting
            point for the audio
        """
        for i in range(1000):
            if(self.datavals[i,0]>0 and self.datavals[i,0]<0.1):
                startRow = i
                break
        return startRow
    
    def startTimer(self):
        """
            Starts the timer that causes the kinematic data to be updated.
            See onTimer for what happens every 'interval' number of milliseconds
        """
        self.timer.Start(interval = 100, oneshot = False)
        
    def onTimer(self,event):
        """
            When the timer expires (every 100 ms), the time is shown to be updated
            on the LCD timer, and the sensor display is updated with new sensor
            positions.  The increment of 40 indices represents a 100 ms jump in time
            because the sample frequency is 400 Hz.
        """
        if(self.index > self.kinInterval[1]):
            self.stop()
        self.lcdTimer.showTime(self.datavals[self.index,0], self.timeLength)
        self.updateSensorDisplay()
        self.spectrogram.updateTimePos(self.datavals[self.index,0])
        for DV in self.dataViewers:
            DV.updateData(self.index - self.kinInterval[0])
        self.index += int(self.fs/10)
        
    def setNewInterval(self,bounds):
        self.stop()
        lowBound = min(bounds)
        highBound = max(bounds)
        if(lowBound < 1 and highBound > self.timeLength-1 and self.fig.enableUserInteraction == False):   
            self.enableButtons()
            reset = True
        else:            
            self.rewindButton.setEnabled(False)
            self.ffButton.setEnabled(False)
            reset = False
        
        self.index = self.find_nearest(self.datavals[:,0],lowBound)
        self.kinInterval = (self.index, self.find_nearest(self.datavals[:,0],highBound))
        self.audioStartOffset = self._headerSize+(int(self.datavals[self.kinInterval[0],0]*self._fps) & (-2))
        self.audioInterval = (self.audioStartOffset, self._headerSize+(int(self.datavals[self.kinInterval[1],0]*self._fps) & (-2)))
        self.audioFile.open(QtCore.QIODevice.ReadOnly)
        self.audioFile.seek(self.audioInterval[0])
        self.lcdTimer.showTime(self.datavals[self.index,0], self.timeLength)
        self.updateSensorDisplay()
        self.spectrogram.updateTimePos(self.datavals[self.index,0])
        
        for sensors in self.allSensors:
            sensors.updateInterval(self.kinInterval[0],self.kinInterval[1])
        
        for DV in self.dataViewers:
            DV.updateInterval(reset)
        
        if(self.trajectoryMode==True):
            self.toggleTrajectoryMode()
        
        self.status = self.stopped
        
    def playPause(self):
        """
            Governs what happens when the play/pause button is pushed.
            Action depends on the current state of the application:
            playing, paused, and stopped
        """
        if(self.status == self.playing):
            #If we are currently playing.. pause and set the icon to play
            self.output.suspend()
            self.playPauseButton.setIcon(QtGui.QIcon(':/play.svg'))
            self.status = self.paused
            pos = self.audioFile.pos()
            self.index = self.find_nearest(self.datavals[:,0],(pos - self._headerSize)/self._fps)
            self.updateSensorDisplay()
            self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
            self.spectrogram.updateTimePos(self.datavals[self.index,0])
            
        elif(self.status == self.paused):
            self.output.resume()
            #If we were stopped or paused, now we are playing again. Show pause
            self.playPauseButton.setIcon(QtGui.QIcon(':/pause.svg'))
            self.status = self.playing
            
        elif(self.status ==self.stopped): #we were stopped and just starting
            if(not self.audioFile.isOpen()):            
                self.audioFile.open(QtCore.QIODevice.ReadOnly)
                self.audioFile.seek(self.audioInterval[0])
                self.output.start(self.audioFile)
            else:
                self.output.start(self.audioFile)
                
            self.playPauseButton.setIcon(QtGui.QIcon(':/pause.svg'))
            self.status = self.playing
        
    def stop(self):
        """
        Handles what happens when stop button is pushed.
        Gotta stop the audio, timer, and set the current status
        """
        self.playPauseButton.setIcon(QtGui.QIcon(':/play.svg'))
        self.status = self.stopped
        self.index = self.kinInterval[0]
        self.timer.Stop()
        if(self.output.state() == QtMultimedia.QAudio.ActiveState):
            self.output.stop()
        if(self.audioFile.isOpen()):
            self.audioFile.close()
        self.lcdTimer.showTime(self.datavals[self.kinInterval[0],0],self.timeLength)
        self.spectrogram.updateTimePos(self.datavals[self.kinInterval[0],0])
        self.updateSensorDisplay()
            
    def stepForward(self):
        """
            StepForward handles what happens when the step forward button is pushed.
        """
        if(self.status != self.stopped):
            self.output.stop()
            self.status = self.stopped
            self.playPauseButton.setIcon(QtGui.QIcon(':/play.svg'))
        if(not self.audioFile.isOpen()):
            self.audioFile.open(QtCore.QIODevice.ReadOnly)
            pos = self.audioInterval[0]
        else:  
            pos = self.audioFile.pos()
        newPos = int(pos+0.05*self._fps)&(-2)
        if(newPos > self.audioInterval[1]):
            self.stop()
            return
        self.audioFile.seek(newPos)
        self.index = self.find_nearest(self.datavals[:,0],(newPos - self._headerSize)/self._fps) #44100 frames/sec
        self.spectrogram.specgram.timePos.get_xdata()
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
        self.spectrogram.updateTimePos(self.datavals[self.index,0])
        self.updateSensorDisplay()
        for DV in self.dataViewers:
            DV.updateData(self.index - self.kinInterval[0])
    
    def stepBackward(self):
        """
            Handles what to do when the step backward button is pushed
        """
        if(self.status != self.stopped):
            self.output.stop()
            self.status = self.stopped
            self.playPauseButton.setIcon(QtGui.QIcon(':/play.svg'))
        if(not self.audioFile.isOpen()):
            self.audioFile.open(QtCore.QIODevice.ReadOnly)
            pos = self.audioInterval[0]
        else:  
            pos = self.audioFile.pos()
        newPos = int(pos-0.05*self._fps)&(-2)
        if(newPos < self.audioInterval[0]):
            self.stop()
            return
        self.audioFile.seek(newPos)
        self.index = self.find_nearest(self.datavals[:,0],(newPos - self._headerSize)/self._fps) #44100 frames/sec
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
        self.spectrogram.updateTimePos(self.datavals[self.index,0])
        self.updateSensorDisplay()
        for DV in self.dataViewers:
            DV.updateData(self.index - self.kinInterval[0])
    
    def fastForward(self):
        """
            Handles what to do when the fast forward button si pushed.
            Jumps forward 5 seconds.
        """
        if(self.status == self.stopped):
            return
            
        self.output.stop()
        pos = self.audioFile.pos()
        newPos = pos + 5*self._fps
        if(newPos > self.audioSize):
            self.stop()
            return
        self.audioFile.seek(newPos)
        self.index = self.find_nearest(self.datavals[:,0],(newPos - self._headerSize)/self._fps) #44100 frames/sec
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
        if(self.status == self.playing):
            self.output.start(self.audioFile)
        elif(self.status == self.paused):
            self.output.start(self.audioFile)
            self.output.suspend()
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
        
    def rewind(self):
        """
            rewinding the file 5 seconds when the button is pushed.
        """
        if(self.status == self.stopped):
            return
            
        self.output.stop()
        pos = self.audioFile.pos()
        newPos = pos - 5*self._fps
        if(newPos < self.audioInterval[0]):
            self.stop()
            return
        self.audioFile.seek(newPos)
        self.index = self.find_nearest(self.datavals[:,0],(newPos - self._headerSize)/self._fps) #44100 frames/sec
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
        if(self.status == self.playing):
            self.output.start(self.audioFile)
        elif(self.status == self.paused):
            self.output.start(self.audioFile)
            self.output.suspend()
        self.lcdTimer.showTime(self.datavals[self.index,0],self.timeLength)
    
    def setupAudioFile(self):
        """
            Sets up the audiofile.  Gets the number of channels, samprate,
            and sets the format of the MultimediaPlayer accordingly.
            When the multimedia players state changes, handlestatechanged is called.
        """
        audioWaveFile = wave.open(self.audiofilename)
        (numChannels, sampwidth, framerate, nframes, _,_) = audioWaveFile.getparams()
        audioWaveFile.close()
        
        audioQFile = QtCore.QFile(self.audiofilename)
        audioQFile.open(QtCore.QIODevice.ReadOnly)
        totalBytes = audioQFile.size()
        audioQFile.close()
        
        self._headerSize = totalBytes - nframes*sampwidth
        self._fs = framerate
        self._bytesPerSample = sampwidth
        self.audioSize = nframes*sampwidth
        self._fps = framerate*sampwidth
        
        self.formats = QtMultimedia.QAudioFormat()
        self.formats.setChannels(numChannels)
        self.formats.setFrequency(self._fs)
        self.formats.setSampleSize(8*self._bytesPerSample)
        self.formats.setCodec("audio/pcm")
        self.formats.setByteOrder(QtMultimedia.QAudioFormat.LittleEndian)
        self.formats.setSampleType(QtMultimedia.QAudioFormat.SignedInt)
        self.output = QtMultimedia.QAudioOutput(self.formats)
        self.audioFile = QtCore.QFile(self.audiofilename)
        self.output.stateChanged.connect(self.handleStateChanged)
        
    def updateSensorDisplay(self):
        """
            Updates where the sensors are shown on screen, as well as their labels
            and orientations based on the position, quaternion data.
            
            The label position changes based on the view.
        """
        for sensors in self.allSensors:
            sensors.updateDataAndText(self.index)
    
    def setInitialSensorDisplay(self):
        """
            Loads the initial sensors from the first part of the kinfile and
            shows them on screen.  The colors are hard coded using the RGB convention
            that gets used in OpenGL.  Can mess with the scaling to change the size
            of the markers on the screen.
        """
        #SensorData comes in as startRow, stopRow+1, name, label
        #You can change this depending on the dataset you are using to make it show
        #other sensor configurations.  Eventually, this will go in a dialog that the user
        #can use to determine the sensor settings, and allow for saving/loading different configs.

        #DDK Setup for subject 3 below:
#        sensorData = [(14,21,'Molar','MM'),
#                      (23,30,'Midsagittal Incisor','MI'),
#                      (32,39,'Tongue Dorsum', 'TD'),
#                      (41,48,'Tongue Blade','TB'),
#                      (50,57,'Lower Lip', 'LL'),
#                      (59,66,'Upper Lip', 'UL')]
                      
        #kinData, axes, name, label,
        #This should eventually get pulled out into a dialog that lets the user
        #input the format of the data.  Then they can load custom file types for display        
        self.allSensors = [sensor.Sensor(self.datavals[:,self.sensorDataFormat[i][0]:self.sensorDataFormat[i][1]],self.axes,self.sensorDataFormat[i][2],
                                         self.sensorDataFormat[i][3],self.fs) for i in xrange(self.numSensors)]
        self.axes.SetLimits(margin = 0.9)
        self.axes.camera.zoom *=1.5
        
        lims = self.axes.GetLimits()
        if(abs(lims[0].max-lims[0].min) < 10):
            xmin = -60
            xmax = 10
            ymin = -20
            ymax = 30
            zmin = -25
            zmax = 25
            self.axes.SetLimits(rangeX = (xmin,xmax),rangeY = (ymin,ymax), rangeZ = (zmin,zmax))
        
    def setupAxes(self):
        """
            Sets up the axes initially.  Shows a 2d view with a range based 
            on the sensor positions.  Might want to give the user the option to set the range
            in future releases.
            The if statement is for when the sensors got switched.. which only
            happens on 2 subjects, but totally messes up the axes view then.
            
        """
        vv.clf()    
        self.axes = vv.gca()
        self.axisLabeler = self.axes.axis
        self.axes.cameraType = 3
        self.axes.daspectAuto= False

        #.SetLimits(#rangeX = (xmin,xmax),rangeY = (ymin,ymax), rangeZ = (zmin,zmax))
        self.axisLabeler.showGrid = True
    
    def handleStateChanged(self,newState):
        """ 
            Based on the audio state, we need to change whether or not the kinematic
            update timer is running.  This is just a reimplemented event handler basically.
        """
        if newState == QtMultimedia.QAudio.ActiveState:
            self.startTimer()
        elif newState == QtMultimedia.QAudio.IdleState:
            self.stop()
        else:
            self.timer.Stop()
            
    def loadTsv(self,kinfilename):
        """
            Loads the tsv file, making A LOT of assumptions about the data.
            If this tool is to work with many different data sets, this will have
            to become safer (use some try, catch blocks) and the data will be 
            different each time.
        """
        data = np.genfromtxt(unicode(kinfilename), skip_header = 1, delimiter = '\t')
        return data
        
    def find_nearest(self,array,value):
        """
            Gets the nearest array index to a certain value passed in.
        """
        
        idx = (np.abs(array-value)).argmin()
        return idx
        
    def showMidsagittalView(self):
        """
            Sets the camera view to midsagittal
            changes offsets for labels and axes labels
            RESET THE ZOOM OF THE CAMERA!!
        """
        self.axes.camera.azimuth = 0
        self.axes.camera.elevation= 90
        self.axes.camera.roll = 0
        
        for sens in self.allSensors:
            sens.updateView('midsagittal')
        
        self.axisLabeler.xLabel = 'Dist w/r/t CMI (X, mm)'
        self.axisLabeler.yLabel = 'Dist w/r/t MOP (Y, mm)'
        self.axisLabeler.zLabel = ''

    
    def showFrontView(self):
        self.axes.camera.azimuth = 90
        self.axes.camera.elevation= 0
        self.axes.camera.roll = 90
        
        for sens in self.allSensors:
            sens.updateView('front')
        
        self.axisLabeler.xLabel = ''
        self.axisLabeler.yLabel = 'Dist w/r/t MOP (Y, mm)'
        self.axisLabeler.zLabel = 'Dist w/r/t MSP (Z, mm)'
        
    def showTopView(self):
        self.axes.camera.azimuth = 180
        self.axes.camera.elevation= 0
        self.axes.camera.roll = -90
        
        for sens in self.allSensors:
            sens.updateView('top')
        
        self.axisLabeler.xLabel = 'Dist w/r/t CMI (X, mm)'
        self.axisLabeler.yLabel = ''
        self.axisLabeler.zLabel = 'Dist w/r/t MSP (Z, mm)'
        
    def showBottomView(self):
        self.axes.camera.azimuth = 0
        self.axes.camera.elevation= 0
        self.axes.camera.roll = 90
        
        for sens in self.allSensors:
            sens.updateView('bottom')
        self.axisLabeler.xLabel = 'Dist w/r/t CMI (X, mm)'
        self.axisLabeler.yLabel = ''
        self.axisLabeler.zLabel = 'Dist w/r/t MSP (Z, mm)'
 
    def resizeEvent(self, event):
        """
            Resizing the window messes with the QTimer used to synchronize the
            audio and the kinematic data.  Because of this, we stop playing
            on a resize and force the user to start playing again, ensuring
            that everything remains synchronized.
            
            Also call the parent class of the resizeEvent, just to make sure 
            other stuff happens that we (don't) care about.
        """
        if(self.fileLoaded):
            self.stepBackward()
            self.stepForward()
        super(DataController, self).resizeEvent(event)
    
    def enableButtons(self):
        """
            Enables the buttons so the user can use them!
        """
        self.playPauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)
        self.ffButton.setEnabled(True)
        self.rewindButton.setEnabled(True)
        self.stepForwardButton.setEnabled(True)
        self.stepBackwardButton.setEnabled(True)
        
    def disableButtons(self):
        """
            Disables the buttons so the user can't use them and cause mischeif
            when the file is loading... those jerks.
        """
        self.playPauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.ffButton.setEnabled(False)
        self.rewindButton.setEnabled(False)
        self.stepForwardButton.setEnabled(False)
        self.stepBackwardButton.setEnabled(False)
        
    def toggleInteractiveMode(self):
        if self.fig.enableUserInteraction == False:
            self.stepBackward()
            self.playPauseButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            self.ffButton.setEnabled(False)
            self.rewindButton.setEnabled(False)
            
        else:
            self.playPauseButton.setEnabled(True)
            self.stopButton.setEnabled(True)
            self.ffButton.setEnabled(True)
            self.rewindButton.setEnabled(True)
        
        self.fig.enableUserInteraction  = not self.fig.enableUserInteraction
        
    def toggleTrajectoryMode(self):
        if(self.trajectoryMode == False):
             for sensors in self.allSensors:
                 sensors.plotIntervalPoints(self.kinInterval[0],self.kinInterval[1])
             
             #Plot all of the sensors in the interval here
        else:
            for sensors in self.allSensors:
                sensors.removeIntervalPoints()
                
            #Remove all of the sensor positions in the interval here
        
        self.trajectoryMode = not self.trajectoryMode
        
    def saveScreenshots(self,filename):
        if(self.status == self.playing):
            self.playPause()
            self.status = self.paused
            
        vv.screenshot(str(filename +'_figure.png'), self.axes)
        self.spectrogram.screenshot(str(filename +'_spec.png'))
        
    def exportIntervalData(self,filename):
        if(self.status == self.playing):
            self.playPause()
            self.status = self.paused
        
        toExport = self.datavals[self.kinInterval[0]:self.kinInterval[1],0]
        headers = 'Time   \t'
        for DV in self.dataViewers:
            toExport = np.column_stack((toExport,DV.speedVals,DV.accelVals))
            headers = headers + str(DV.id) + ' speed\t' + str(DV.id) + ' accel\t'
              
        np.savetxt(str(filename+'.tsv'), toExport, header= headers, fmt = '%8.3f', delimiter = '\t')
         
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
    """
        Just a little testing method in case you want to test the widget on
        its own and not load a full blown application with it.
        Will probably have to change the audiofile and kinfile to make it work
        on any given system.
    """
    backend = 'pyqt4'
    app = vv.use(backend)
    audiofile = "C:\\MATLAB_Workspace\\TongueMesh\\data\\calibration\\TMD_palate.wav"
    kinfile =  "C:\\MATLAB_Workspace\\TongueMesh\\data\calibration\\TMD_palate_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    form = DataController(kinfile,audiofile,400)
    form.show()
    sys.exit(qtApp.exec_())