
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 19:35:29 2015

@author: Andrew
"""

from PyQt4 import QtGui
import numpy as np

class LcdTimer(QtGui.QLCDNumber):
    def __init__(self, parent=None):
        super(LcdTimer, self).__init__(parent)

        #Make it look pretty!
        self.setSegmentStyle(QtGui.QLCDNumber.Filled)
        palette = self.palette()
        palette.setColor(palette.WindowText, QtGui.QColor(102,255,255))
        palette.setColor(palette.Background, QtGui.QColor('black'))
        palette.setColor(palette.Light, QtGui.QColor(51,0,102))
        palette.setColor(palette.Dark, QtGui.QColor('black'))
        self.setPalette(palette)
        self.setDigitCount(18)
        self.resize(400, 60)
        
        #Set up the time variable and show it on the clock.
        self.time = 0

    def showTime(self,seconds, maxseconds):
        self.time = seconds
        self.maxtime = maxseconds
        displayTime = '%02d:%02d.%02d-%02d:%02d.%02d' % (self.time // 60, round(np.modf(self.time)[1]) % 60, (round(np.modf(self.time)[0],2)*100)%100,
                                                            self.maxtime // 60, round(np.modf(self.maxtime)[1]) % 60, (round(np.modf(self.maxtime)[0],2)*100)%100)
        self.display(displayTime)
        
if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    clock = LcdTimer()
    clock.show()
    clock.showTime(24.234,65.232)
    sys.exit(app.exec_())