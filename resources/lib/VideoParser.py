#   Copyright (C) 2011 Jason Anderson
#
#
# This file is part of PseudoTV.
#
# PseudoTV is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PseudoTV is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PseudoTV.  If not, see <http://www.gnu.org/licenses/>.

import xbmc
import os, platform
import subprocess

import VideoParserFFProbe as VideoParserFFProbe

import Globals, xbmcvfs
from FileAccess import FileAccess
from Globals import *

class VideoParser:
    def __init__(self):
        self.Exts = ['.mkv', '.mp4', '.m4v', '.3gp', '.3g2', '.f4v', '.mov', '.avi', '.flv', '.ts', '.m2ts']
        self.durationFile = xbmcvfs.translatePath(os.path.join(Globals.SETTINGS_LOC, 'filedurations.txt'))
        
        
    def log(self, msg, level = xbmc.LOGDEBUG):
        log('VideoParser: ' + msg, level)


    def getVideoLength(self, filename):
        self.log("getVideoLength " + str(filename))

        if len(filename) == 0:
            self.log("No file name specified")
            return 0

        if FileAccess.exists(filename) == False:
            self.log("Unable to find the file")
            return 0

        fileDuration = self.readDurationFile(filename)
        if fileDuration == False:
        
            base, ext = os.path.splitext(filename)
            ext = ext.lower()

            if ext in self.Exts:
                self.parser = VideoParserFFProbe.VideoParserFFProbe()
            
            else:    
                self.log("Unsupported extension " + str(ext))
                return 0

            #try:
                
            duration = self.parser.determineLength(filename)
            if duration != 0:
                self.writeDuration(filename, duration)
            
            return duration
            
            #except:
            #    self.log("Exception trying FFPROBE - see ReadMe on installing FFMEG")
            #    return 0
        
        else:
            return fileDuration

    def readDurationFile(self, filename):
        self.log('RDF readDurationFile: ' + filename)
        if FileAccess.exists(self.durationFile):
            
            with open(self.durationFile, 'r') as fp:
                for l_no, line in enumerate(fp):
                    # search string
                    # self.log('RDF line: :' + str(line))
                    
                    if filename in line:
                        #self.log('RDF string found in a file')
                        #self.log('RDF Line Number: ' + str(l_no))
                        #self.log('RDF Line: ' +  str(line))
                        
                        splitLine=line.split('|')
                        duration = float(splitLine[1])
                        
                        self.log('RDF duration: ' + str(duration))
                        return int(duration)
                        # don't look for next lines
                        break
                else:
                    self.log('RDF readDurationFile - No Match')
                    return False
        else:
            self.log('RDF no file yet')
            return False            
    
    
    def writeDuration(self, filename, duration):
        if FileAccess.exists(self.durationFile):
            self.log('writeDuration found file, append')
            append_write = 'a' 
        else:
            self.log('writeDuration file not found, make new')
            append_write = 'w' 
        
        fle = open(self.durationFile, append_write, encoding="utf-8")
        
        flewrite = (Globals.uni(filename) + "|" + Globals.uni(str(duration))   + "\n")

        fle.write(flewrite)
        fle.close()        
        
        
        #except:
        #    self.log("Unable to open the duration file for writing")
        #    return

        

