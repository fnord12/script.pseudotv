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
import os, struct
import traceback

from Globals import ascii
from FileAccess import FileAccess

import subprocess



class VideoParserFFProbe:
    def log(self, msg, level = xbmc.LOGDEBUG):
        xbmc.log('script.pseudotv-VideoParserFFProbe: ' + ascii(msg), level)


    def determineLength(self, filename):
        
        
        
        result = subprocess.run(["ffprobe", "-v", "quiet", "-show_entries",
                                 "format=duration", "-of", 
                                 "default=noprint_wrappers=1:nokey=1", filename], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        
        
        tempDur = str(result.stdout)
        self.log ('result.stdout: ' + tempDur)
        
        
        if ('Header missing' in tempDur) or ('invalid' in tempDur) or ('Invalid' in tempDur):
            self.log ('Header missing')
            spiltDur = tempDur.split('\\',1)
            spiltDur = spiltDur[0].split('\'',1)
            durationfloat = float(spiltDur[1])
            self.log ('durationfloat= ' + str(durationfloat))
        else:
            try:
                durationfloat = float(result.stdout)
            except:
                self.log("Exception attempting to convert duration to float: " + filename + " " + str(result.stdout))
                durationfloat = 0
            
        duration = int(durationfloat)
        
        self.log ('determined length for ' + filename + ' is: ' + str(duration))
            
        return duration
