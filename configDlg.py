# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 2015 13:46:32 2015

@author: Andrew Kolb
"""

from PyQt4 import QtCore, QtGui
import sys

class ConfigDlg(QtGui.QDialog):
    
    def __init__(self,  configList = None, parent = None):
        super(ConfigDlg,self).__init__(parent)
        
        #configList should be dict
        #key is name
        #values are tuples of the parameters
        
        #Left side will have previous configuations to load
        self.configs = configList
        print self.configs
        self.configList = QtGui.QListWidget()
        if self.configs is not None:
            self.configList.addItems(self.configs.keys())
        self.currentNumSensors = 1
        savedConfigLabel = QtGui.QLabel('Saved Configurations ')
        loadButton = QtGui.QPushButton('Load')
        deleteButton = QtGui.QPushButton('Delete')
        
        leftLayout = QtGui.QVBoxLayout()
        leftLayout.addWidget(savedConfigLabel)
        leftLayout.addWidget(self.configList)
        leftLayout.addWidget(loadButton)
        leftLayout.addWidget(deleteButton)
        
        
        #Right side will have the current configuration
        newConfigLabel = QtGui.QLabel('<b> Current Configuration Data </b>')
        newConfigLabel.setAlignment(QtCore.Qt.AlignCenter)
        configName = QtGui.QLabel('Configuration Name: ')
        self.configNameEdit = QtGui.QLineEdit()
        numSensorLabel = QtGui.QLabel('# of Sensors (excl. REF sensor)')
        fsLabel = QtGui.QLabel('Fs')
        self.fsSpinBox = QtGui.QSpinBox()
        self.fsSpinBox.setRange(100,400)
        self.fsSpinBox.setSingleStep(100)
        self.numSensorSpinBox = QtGui.QSpinBox()
        self.numSensorSpinBox.setRange(1,7)
        self.sensorInfos = [SensorInfoUI(1,self)]
        saveButton = QtGui.QPushButton('Save')
        continueButton = QtGui.QPushButton('Use Current Config')
        topLayout = QtGui.QHBoxLayout()
        topLayout.addWidget(configName)
        topLayout.addWidget(self.configNameEdit)
        topLayout.addWidget(numSensorLabel)
        topLayout.addWidget(self.numSensorSpinBox)
        topLayout.addWidget(fsLabel)
        topLayout.addWidget(self.fsSpinBox)
        bottomLayout = QtGui.QHBoxLayout()
        bottomLayout.addStretch()
        bottomLayout.addWidget(saveButton)
        bottomLayout.addWidget(continueButton)
        self.sensorLayout = QtGui.QVBoxLayout()
        self.sensorLayout.addWidget(self.sensorInfos[0])
        self.rightLayout = QtGui.QVBoxLayout()
        self.rightLayout.addWidget(newConfigLabel)
        self.rightLayout.addLayout(topLayout)
        self.rightLayout.addLayout(self.sensorLayout)
        self.rightLayout.addStretch()
        self.rightLayout.addLayout(bottomLayout)
        
        #Save and update buttons go here
        self.finalLayout = QtGui.QHBoxLayout()
        self.finalLayout.addLayout(leftLayout)
        self.finalLayout.addLayout(self.rightLayout)
        self.setLayout(self.finalLayout)
        self.setWindowTitle('Configuration Dialog')
        
        self.connect(self.numSensorSpinBox,QtCore.SIGNAL("valueChanged(int)"),self.updateNumSensors)
        self.connect(deleteButton,QtCore.SIGNAL("clicked()"), self.deleteConfig)        
        self.connect(loadButton, QtCore.SIGNAL("clicked()"), self.loadConfig)        
        self.connect(saveButton, QtCore.SIGNAL("clicked()"), self.saveConfig)        
        self.connect(continueButton, QtCore.SIGNAL("clicked()"), QtCore.SLOT("accept()"))
        
    def updateNumSensors(self):
        numSensors = self.numSensorSpinBox.value()
        diff = numSensors - self.currentNumSensors
        
        if(diff>0):
            for i in range(self.currentNumSensors+1,numSensors+1):
                self.sensorInfos.append(SensorInfoUI(i,self))
                self.sensorLayout.addWidget(self.sensorInfos[i-1])
                self.sensorInfos[i-1].show()
        else:
            for i in reversed(range(numSensors,self.currentNumSensors)):
                self.sensorInfos[-1].setParent(None)
                self.sensorInfos.remove(self.sensorInfos[-1])
        
        self.currentNumSensors = numSensors
        
    def deleteConfig(self):
        #Maybe ask the user if they are sure they want to delete a configuration
        self.configs.pop(QtCore.QString(unicode(self.configList.currentItem().text())))
        self.configList.takeItem(self.configList.row(self.configList.currentItem()))
        self.configNameEdit.setText('')
        for i in range(self.currentNumSensors):
            self.sensorInfos[i].nameEdit.setText('')
            self.sensorInfos[i].labelEdit.setText('')
        self.numSensorSpinBox.setValue(1)

        
    def loadConfig(self):
        toLoad = QtCore.QString(self.configList.currentItem().text())
        if(toLoad is None):
            return
        
        fs = self.configs[toLoad][0]
        numSensors = self.configs[toLoad][1]
        names = self.configs[toLoad][2]
        labels = self.configs[toLoad][3]
        self.configNameEdit.setText(toLoad)
        self.fsSpinBox.setValue(fs)
        self.numSensorSpinBox.setValue(numSensors)
        for i in range(self.currentNumSensors):
            self.sensorInfos[i].nameEdit.setText(names[i])
            self.sensorInfos[i].labelEdit.setText(labels[i])
        
    def saveConfig(self):
        newKey, data = self.getData()
        if False in (newKey, data):
            return
        
        if self.configs is not None:
            if newKey in self.configs.keys():
                questionDlg = QtGui.QMessageBox.question(self,'Duplicate Title',
                                     "A configuration currently has the same name, would you like to overwrite?",
                                     QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
                if questionDlg == QtGui.QMessageBox.Yes:
                    self.configs[newKey] = data

                return
        if self.configs is None:
            self.configs = {}
        self.configs[newKey] = data
        self.configList.addItem(newKey)
        
    def getData(self):
        newKey = str(self.configNameEdit.text())
        names = tuple(str(self.sensorInfos[i].nameEdit.text()) for i in range(self.currentNumSensors))
        labels = tuple(str(self.sensorInfos[i].labelEdit.text()) for i in range(self.currentNumSensors))
        data = (self.fsSpinBox.value(), self.numSensorSpinBox.value(),names,labels)
        
        if '' in names or '' in labels:
            QtGui.QMessageBox.warning(self,'Invalid Input', 'No fields can be left empty')
            return False, False
        
        return newKey, data
    
    def sendConfigs(self):
        return self.configs
        
    def closeEvent(self, evnt):
        evnt.ignore()
        #self.setWindowState(QtCore.Qt.WindowMinimized)
    def accept(self):
        newKey, data = self.getData()
        if(not newKey or not data):
            return
        else:
            super(ConfigDlg, self).accept()

        
class SensorInfoUI(QtGui.QWidget):
    
    def __init__(self, number, parent = None):
        super(SensorInfoUI,self).__init__(parent)
        
        numberLabel = QtGui.QLabel('<b> Sensor %i Info </b>' % number)
        nameLabel = QtGui.QLabel('Name: ')
        self.nameEdit = QtGui.QLineEdit()
        labelLabel = QtGui.QLabel('Label: ')
        self.labelEdit = QtGui.QLineEdit()
        self.labelEdit.setMaxLength(2)
        
        layout = QtGui.QHBoxLayout()
        layout.addWidget(nameLabel)
        layout.addWidget(self.nameEdit)
        layout.addWidget(labelLabel)
        layout.addWidget(self.labelEdit)
        
        finalLayout = QtGui.QVBoxLayout()
        finalLayout.addWidget(numberLabel)
        finalLayout.addLayout(layout)
        self.setLayout(finalLayout)
        
if __name__ == '__main__':
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    configList = {'RASS': (100, 5,('Upper Lip','Lower Lip','Tongue Dorsum','Tongue Blade','Medial Incisor'),('UL','LL','TD','TB','MI')),
                 'DDK':  (100, 6,('Molar','Medial Incisor','Tongue Dorsum','Tongue Blade','Lower Lip','Upper Lip'),('MM','MI','TD','TB','LL','UL')),
                 'EMA-MAE': (400, 7,('Tongue Dorsum','Tongue Lateral','Tongue Blade','Upper Lip','Lower Lip','Lip Corner','Medial Incisor'),('TD','TL','TB','UL','LL','LC','MI'))}
                  
    form = ConfigDlg(configList)
    form.show()
    sys.exit(qtApp.exec_())