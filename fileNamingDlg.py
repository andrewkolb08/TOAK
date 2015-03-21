# -*- coding: utf-8 -*-
"""
Created on Fri Feb 20 13:46:32 2015

@author: speechlab
"""

from PyQt4 import QtCore, QtGui
import os
import sys

class FileNamingDialog(QtGui.QDialog):
    
    def __init__(self, currentFile, item='File', currentDir = None, parent = None):
        super(FileNamingDialog,self).__init__(parent)
        
        self.currentFile = currentFile
        drive, path = os.path.splitdrive(self.currentFile)
        path, filename = os.path.split(path)
        filename, ext = os.path.splitext(filename)
        
        dirLabel = QtGui.QLabel("Folder: ")
        if(currentDir is None):
            self.dirInputBox = QtGui.QLineEdit(QtCore.QString(os.path.join(drive,path)))
        else:
            self.dirInputBox = QtGui.QLineEdit(QtCore.QString(currentDir))
            
        browseButton = QtGui.QPushButton("Browse...")
        fileLabel = QtGui.QLabel("File name:")
        self.fileInputBox = QtGui.QLineEdit(QtCore.QString(filename))
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Cancel)

        layout = QtGui.QGridLayout()
        layout.addWidget(dirLabel,0,0)
        layout.addWidget(self.dirInputBox,0,1)
        layout.addWidget(browseButton,0,2)
        layout.addWidget(fileLabel,1,0)
        layout.addWidget(self.fileInputBox,1,1)
        layout.setColumnStretch(1,3)
        layout.addWidget(buttonBox,2,1,1,2)
        self.resize(400,100)
        self.setWindowTitle('Save '+ item + ' As...')
        self.setLayout(layout)
        
        
        self.connect(buttonBox,QtCore.SIGNAL("accepted()"), self, QtCore.SLOT("accept()"))
        self.connect(buttonBox, QtCore.SIGNAL("rejected()"), self, QtCore.SLOT("reject()"))
        self.connect(browseButton,QtCore.SIGNAL("clicked()"), self.selectDir)

    def selectDir(self):
        dir = os.path.dirname(unicode(self.currentFile))\
        if self.currentFile is not None else "."
        dirToSaveIn = QtCore.QString(QtGui.QFileDialog.getExistingDirectory(self,
                            "Visualization Tool - Choose Folder", dir,
                            QtGui.QFileDialog.ShowDirsOnly))                    
        if dirToSaveIn is not QtCore.QString():
            self.dirInputBox.setText(dirToSaveIn)
        
    def getFile(self):
        dirname = unicode(self.dirInputBox.text())
        filename = unicode(self.fileInputBox.text())
        return QtCore.QString(os.path.join(dirname,filename))
        
        
if __name__ == '__main__':
    kinfile =  "C:/Data/05_ENGL_F_words6_BPC.tsv"
    qtApp = QtGui.QApplication(sys.argv)
    form = FileNamingDialog(kinfile,'Images')
    form.show()
    form.getFile()
    sys.exit(qtApp.exec_())