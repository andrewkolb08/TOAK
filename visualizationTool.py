# -*- coding: utf-8 -*-
"""
Created on Mon Jan 19 14:18:53 2015

@author: Andrew
"""

import os
import sys
from PyQt4 import QtCore, QtGui
import qrc_resources
import dataController as DC
import copy
import fileNamingDlg as fnd
import numpy as np

__version__ = "1.0.0"


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
#        """
#        This represents the main window of the VisualizationTool (which doesn't yet have a real name).
#        The main window holds several widgets, including: the data controller, specWidget, and
#        sensorDataViewer.  The dataController is the class governing the playing, pausing, fast-forwarding, 
#        rewinding, etc. The specWidget allows for a view of audio data's frequency content.  The dataViewer
#        shows the speed, accelaration and range for a given sensor, which is labeled at the top.
#        See any of these for reference.
#        Aside from the central dataController widget, there is a toolbar that allows for loading a file
#        and changing the view of the dataController's figure.  The views include, top, bottom, midsagittal
#        and front.
#        In version 1.5, there is another view, the 3D view, which allows for arbitrary views of the data to be
#        seen.  Using the mouse buttons and scroll buttons, you can look at the sensors from any angle.  You can 
#        also zoom in and out using the scroll wheel on the mouse, and change the focus using by holding shift and
#        moving the mouse in the desired direction.
#
#        """
        super(MainWindow, self).__init__(parent)
        np.set_printoptions(precision=2, suppress=True)
        self.audiofilename = None#"C:/Data/05_ENGL_F_words6.wav"
        self.kinfilename =  None#"C:/Data/05_ENGL_F_words6_BPC.tsv"
        
        self.dataController = DC.DataController(self.kinfilename,self.audiofilename,400)
        self.dataController.setMinimumSize(700,700)        
        self.center()
#        self.dataController.setAlignment(QtCore.Qt.AlignCenter)
#        self.imageLabel.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.setCentralWidget(self.dataController)
        self.dataController.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        status = self.statusBar()
        status.setSizeGripEnabled(False)
        status.showMessage("Ready", 5000)

        fileOpenAction = self.createAction("&Open...", self.fileOpen,
                QtGui.QKeySequence.Open, "fileopen",
                "Open a kinematic file")
        fileQuitAction = self.createAction("&Quit", self.close,
                "Ctrl+Q", "filequit", "Close the application")
                                                  
        self.fileMenu = self.menuBar().addMenu("&File")
        self.fileMenuActions = (fileOpenAction, None, fileQuitAction)
        self.addActions(self.fileMenu,self.fileMenuActions)
        
        fileToolbar = self.addToolBar("File")
        fileToolbar.setObjectName("FileToolBar")
        self.addActions(fileToolbar, (fileOpenAction,None))
        
        self.midsagittalView = True
        self.frontView = False
        self.topView = False
        self.bottomView = False
        self.showTrajectory = False
        self.threeDView = False
        
        viewGroup = QtGui.QActionGroup(self)
        
        midSagittalViewAction = self.createAction("&Midsagittal View",
            self.showMidsagittalView, "Ctrl+M", "mid","Show midsagittal view",True,"toggled(bool)")
        viewGroup.addAction(midSagittalViewAction)
        
        topViewAction = self.createAction("&Top View",
            self.showTopView, "Ctrl+T", "top","Show top view",True,"toggled(bool)")
        viewGroup.addAction(topViewAction)
        
        bottomViewAction = self.createAction("&Bottom View",
            self.showBottomView, "Ctrl+B", "bottom","Show bottom view",True,"toggled(bool)")
        viewGroup.addAction(bottomViewAction)
        
        frontViewAction = self.createAction("&Front View",
            self.showFrontView, "Ctrl+F", "front","Show front view",True,"toggled(bool)")
        viewGroup.addAction(frontViewAction)
        
        threeDViewAction = self.createAction("&3D View", self.enable3D, "Ctrl+D", "3D", "Enable 3D View",
                                             True, "toggled(bool)")
        viewGroup.addAction(threeDViewAction)        
        
        
        viewTrajectoryAction = self.createAction("Show Trajectories", self.toggleTrajectories, None, "clock", 
                                                "Show Sensor Trajectories")
        
        viewMenu = self.menuBar().addMenu("&View")
        viewMenuActions = (midSagittalViewAction,topViewAction,bottomViewAction,frontViewAction,threeDViewAction,None,viewTrajectoryAction)
        self.addActions(viewMenu,viewMenuActions)
        
        viewToolBar = self.addToolBar("View")
        viewToolBar.setObjectName("ViewToolBar")
        self.addActions(viewToolBar,(viewMenuActions))   
    
        screenshotAction = self.createAction("Screenshot Figures", self.takeScreenshot, None, "camera",
                                             "Take a screenshot of figures")
        exportSensorDataAction = self.createAction("Export Sensor Data", self.exportIntervalData, None, "export",
                                                   "Export speed/accel data to file")
                                             
        exportMenu = self.menuBar().addMenu("Export")
        exportMenuActions = (screenshotAction,exportSensorDataAction)
        self.addActions(exportMenu,exportMenuActions)
        
        exportToolBar = self.addToolBar("Export")
        exportToolBar.setObjectName("ExportToolBar")
        self.addActions(exportToolBar,exportMenuActions)
        
        self.resetableActions = ((midSagittalViewAction,True),(topViewAction,False),(bottomViewAction,False),(frontViewAction,False),(threeDViewAction,False), (viewTrajectoryAction, False)) 
        
        helpHelpAction = self.createAction("&Help", self.helpHelp, QtGui.QKeySequence.HelpContents)
        helpMenu = self.menuBar().addMenu("&Help")
        self.addActions(helpMenu, (helpHelpAction,None))
        self.setWindowTitle("Visualization Tool")

            
    def createAction(self, text, slot=None, shortcut=None, icon=None,
                     tip=None, checkable=False, signal="triggered()"):
        """
            Just a helper method to create an action and avoid a bunch of extra coding
        """
        action = QtGui.QAction(text, self)
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, QtCore.SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action

    def addActions(self, target, actions):
        """
        Adds actions to the menubar.  Can put a spacer by passing None
        """
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def fileOpen(self):
        """
            The fileOpen method allows a user to choose any file from the file path
            to be played.  The kinfile is found by the user, and the audiofile
            is found by walking backward through the file path (see: self.findAudioFile())
            
            If no audiofile is found, then the user will be prompted to supply it.
            The user has the option to cancel at any time.
            When the file is chosen, the dataController's onFileLoaded is called to
            actually load the data so it can be played back.
            
            The actions are then reset to the midsagittal view, and the status bar at the
            bottom of the program shows that the file was successfully loaded.
            The title of the window is also changed to reflect the file name being played.
        """
        if(self.dataController.status == self.dataController.playing):
            self.showMidsagittalView()
            self.dataController.stop()
        dir = os.path.dirname(unicode(self.kinfilename)) \
                if self.kinfilename is not None else "."
        self.kinfilename = QtCore.QString(QtGui.QFileDialog.getOpenFileName(self,
                            "Visualization Tool - Choose Kinematic File", dir,
                            "TSV files (*.tsv)"))
        if(self.kinfilename == QtCore.QString()):
            return
        newkinfilename = copy.deepcopy(self.kinfilename)
        kinfileEnd = QtCore.QRegExp("_BPC.tsv")
        self.audiofilename = newkinfilename.replace(kinfileEnd,'.wav')
        self.audiofilename = self.findAudioFile(unicode(self.kinfilename))
        if self.audiofilename is None:
            QtGui.QMessageBox.warning(self,'Cannot Find Audio File',
                                     "The corresponding audio file (*.wav) could not be found."
                                     "<p>Please select the corresponding file.",
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
            self.audiofilename = QtCore.QString(QtGui.QFileDialog.getOpenFileName(self,
                            "Visualization Tool - Choose Audio File", dir,
                            "WAV files (*.wav)"))
        if (self.audiofilename is not QtCore.QString()):
            self.dataController.onFileLoaded(unicode(self.kinfilename),unicode(self.audiofilename))
            self.updateStatus("File %s loaded" % unicode(self.kinfilename))
            self.showMidsagittalView()
            self.showTrajectory = False
            self.imageSavingDir = None
            self.textSavingDir = None
            for action, check in self.resetableActions:
                action.setChecked(check)
        else:
            return
            
    def updateStatus(self, message):
        """
            Simply updates the status bar with the message parameter
        """
        self.statusBar().showMessage(message, 5000)
        if self.kinfilename is not None:
            self.setWindowTitle("Visualization Tool - %s" % \
                                os.path.basename(unicode(self.kinfilename)))
                                
    def showMidsagittalView(self):
        """
            Shows the midsagittal view and resets the actions the way we want
        """
        if(self.dataController.fileLoaded == True):    
            self.dataController.showMidsagittalView()
        self.midsagittalView = True
        self.frontView = False
        self.topView = False
        self.bottomView = False
        
    def showTopView(self):
        """
            Shows the topView and resets the actions the way we want
        """
        if(self.dataController.fileLoaded == True):    
            self.dataController.showTopView()
        self.midsagittalView = True
        self.frontView = False
        self.topView = False
        self.bottomView = False
        
    def showBottomView(self):
        """
            Shows the bottom view and resets the actions
        """
        if(self.dataController.fileLoaded == True):    
            self.dataController.showBottomView()
        self.midsagittalView = False
        self.frontView = False
        self.topView = False
        self.bottomView = True
        
    def showFrontView(self):
        """
            Shows the front view and resets the actions
        """
        if(self.dataController.fileLoaded == True):
            self.dataController.showFrontView()
#        self.midsagittalView = False
#        self.frontView = True
#        self.topView = False
#        self.bottomView = False
        
    def enable3D(self):
        """
            Allows for 3d interaction with the data.
            Pretty nifty.
        """
        if(self.dataController.fileLoaded==True):
            self.dataController.toggleInteractiveMode()

        self.midsagittalView = False
        self.frontView = False
        self.topView = False
        self.bottomView = False
        self.threeDView = True
        
    def toggleTrajectories(self):
        if(self.dataController.fileLoaded==True):
            self.dataController.toggleTrajectoryMode()
        self.showTrajectory = not self.showTrajectory
    
    def takeScreenshot(self):
        if(self.dataController.fileLoaded == True):
            
            if(self.imageSavingDir is None):
                fileNamingDialog = fnd.FileNamingDialog(self.audiofilename,'Images')           
            else:
                fileNamingDialog = fnd.FileNamingDialog(self.audiofilename,'Images', self.imageSavingDir)
                
            if fileNamingDialog.exec_():
                filename = fileNamingDialog.getFile()
                self.dataController.saveScreenshots(filename)
                self.imageSavingDir, _ = os.path.split(str(filename))
                QtGui.QMessageBox.information(self,'Save Screenshot',
                                     "Screenshot successfully saved",
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)

    def exportIntervalData(self):
        if(self.dataController.fileLoaded == True):
            
            if(self.textSavingDir is None):
                fileNamingDialog = fnd.FileNamingDialog(self.audiofilename,'Sensor Data')           
            else:
                fileNamingDialog = fnd.FileNamingDialog(self.audiofilename,'Sensor Data', self.textSavingDir)
                
            if fileNamingDialog.exec_():
                filename = fileNamingDialog.getFile()
                self.dataController.exportIntervalData(filename)
                self.textSavingDir, _ = os.path.split(str(filename))
                QtGui.QMessageBox.information(self,'Data Export',
                                     "Data successfully exported",
                                     QtGui.QMessageBox.Ok, QtGui.QMessageBox.NoButton)
        
    def helpHelp(self):
        """
            Shows a dialog (in HTML) that tells people to ask me for help if
            they need it.
        """
        QtGui.QMessageBox.about(self, "Help me!","""
        <p> Program sucks and you need help?
        <p>Email: 
        <p><b>andrew.kolb@marquette.edu</b>
        <p>Or visit him in Room 230U!
        """)
        
    def center(self):
        """
            Method to center the main window on the screen.  Pulled it off
            of stackoverflow, but pretty dope.
        """
        frameGm = self.frameGeometry()
        screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        centerPoint = QtGui.QApplication.desktop().screenGeometry(screen).center()
        frameGm.moveCenter(centerPoint)
        self.move(frameGm.topLeft())    
        
    def findAudioFile(self,kinfilename):
        """
            Funcition for walking backward through the file path to find the matching
            audiofile to match the kinematic file.  Try not to get too confused
            by all the nested for loops...
        """
        (filename, _) = os.path.splitext(os.path.basename(kinfilename))
        pattern = filename.split('_BPC')[0] + '.wav'
        fullpath = os.path.dirname(kinfilename)
        toSearch = []
        audiofilename = None
        for i in self.find(fullpath,'/'):
            toSearch.append(fullpath[:i])
            toSearch.reverse()
        toSearch.append(fullpath)
        for loc in toSearch:
            for filenames in os.walk(loc):
                for filename in filenames:
                    if pattern in filename:
                        desiredFile = filename
                        for files in desiredFile:
                            if pattern == files:
                                audiofilename = os.path.join(filenames[0],files)
                                return audiofilename
        if audiofilename is None:
            return audiofilename
            
    def find(self,s, ch):
        """
            Finds each of the instances of a given character, ch, in the string, s
        """
        return [i for i, ltr in enumerate(s) if ltr == ch]

def main():
    """
        Just sets up the application and runs it!
    """
    qApp = QtGui.QApplication(sys.argv)
    qApp.setApplicationName("Visualization Tool")
    qApp.setOrganizationName("Marquette University Speechlab")
    qApp.setWindowIcon(QtGui.QIcon(":/vtIcon.ico"))
    form = MainWindow()
    form.show()
    sys.exit(qApp.exec_())


main()

