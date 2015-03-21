# -*- coding: utf-8 -*-
"""
Created on Mon Feb 16 19:52:59 2015

@author: speechlab
"""

from PyQt4 import QtCore


class GenericThread(QtCore.QThread):
    def __init__(self, function, *args, **kwargs):
        QtCore.QThread.__init__(self)
        self.function = function
        self.args = args
        self.kwargs = kwargs
 
    def run(self):
         self.function(*self.args,**self.kwargs)
         return