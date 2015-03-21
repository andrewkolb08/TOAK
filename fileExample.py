# -*- coding: utf-8 -*-
"""
Created on Wed Jan 21 11:37:40 2015

@author: speechlab
"""

import os

def findAudioFile(kinfilename):
    
    (filename, _) = os.path.splitext(os.path.basename(kinfilename))
    pattern = filename.split('_BPC')[0] + '.wav'
    fullpath = os.path.dirname(kinfilename)
    toSearch = []
    for i in find(fullpath,'/'):
        toSearch.append(fullpath[:i])
    toSearch.reverse()
    audiofilename = None
    for loc in toSearch:
        for filenames in os.walk(loc):
            for filename in filenames:
                if pattern in filename:
                    desiredFile = filename
                    for files in desiredFile:
                        if pattern == files:
                            print filenames[0]
                            print files
                            audiofilename = os.path.join(filenames[0],files)
                            return audiofilename
    
def find(s, ch):
    return [i for i, ltr in enumerate(s) if ltr == ch]

audiofilename = findAudioFile('C:/EAGER_FINAL_062714/05_ENGL_F/Kinematic/Corrected/05_ENGL_F_words3_BPC.tsv')
print audiofilename