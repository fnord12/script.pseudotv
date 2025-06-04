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

import xbmc, xbmcgui, xbmcvfs
import subprocess, os
import time, threading
import datetime
import sys, re
import random, traceback
import json

from xml.dom.minidom import parse, parseString
from ResetWatched import ResetWatched

from Playlist import Playlist
from Globals import *
from Channel import Channel
from EPGWindow import EPGWindow
from ChannelList import ChannelList
from ChannelListThread import ChannelListThread
from FileAccess import FileLock, FileAccess
from Migrate import Migrate
try:
    from PIL import Image, ImageEnhance
except:
    pass

class MyPlayer(xbmc.Player):
    def __init__(self):
        #xbmc.Player.__init__(self, xbmc.Player()
        xbmc.Player.__init__(self)
        self.stopped = False
        self.ignoreNextStop = False
        self.watchedList = []        

    def log(self, msg, level = xbmc.LOGDEBUG):
        log('Player: ' + msg, level)

    def onPlayBackStopped(self):
        if self.stopped == False:
            self.log('Playback stopped')

            if self.ignoreNextStop == False:
                if self.overlay.sleepTimeValue == 0:
                    self.overlay.sleepTimer = threading.Timer(1, self.overlay.sleepAction)

                self.overlay.sleepTimeValue = 1
                self.overlay.startSleepTimer()
                self.stopped = True
            else:
                self.ignoreNextStop = False

    def onAVChange(self):
        self.log('entering PSTV onAVChange')
        if self.isPlayingVideo():
            if ADDON.getSettingBool("ResetWatched"):
                self.writeWatched()
        else:
            self.log('no video playing')
        if str(self.overlay.currentChannel) in self.overlay.languageChangeChannel:
            self.getDetails()
            lang = str(self.selected_audio_stream['language'])
            lang2 = str(self.overlay.languageChange[0])
            self.log('lang = ' + lang)
            self.log('lang2 = ' + lang2)
            if not lang == lang2:
                self.log('Player: changing audio for channel = ' + str(self.overlay.currentChannel))
                self.overlay.changeAudio(lang2)
        elif str(self.overlay.currentChannel) in self.overlay.languageChangeChannel2:
            self.getDetails()
            lang = str(self.selected_audio_stream['language'])
            lang2 = str(self.overlay.languageChange2[0])
            if not lang == lang2:
                self.log('Player2: changing audio for channel = ' + str(self.overlay.currentChannel))
                self.overlay.changeAudio(lang2)
            
    def writeWatched(self):
        self.log('entering PSTV writeWatched')
        path = xbmc.getInfoLabel('Player.Filenameandpath')
        if (path) and (not path in self.watchedList):
            self.watchedList.append(path)
        self.log('watchedList = ', self.watchedList)
        return
    
    def getDetails(self):
        self.log('entering getDetails')
        activePlayers ='{"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "id": 1}'
        json_query = xbmc.executeJSONRPC(activePlayers)
        json_response = json.loads(json_query)
        activePlayerID = json_response['result'][0]['playerid']
        details_query_dict = {  "jsonrpc": "2.0",
                                "method": "Player.GetProperties",
                                "params": { "properties": 
                                            ["currentaudiostream", "audiostreams", "subtitleenabled",
                                             "currentsubtitle", "subtitles" ],
                                            "playerid": activePlayerID },
                                "id": 1}
        details_query_string = json.dumps(details_query_dict)
        json_query = xbmc.executeJSONRPC(details_query_string)
        json_response = json.loads(json_query)
        if json_response.has_key('result') and json_response['result'] != None:
            self.selected_audio_stream = json_response['result']['currentaudiostream']
    
# overlay window to catch events and change channels
class TVOverlay(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.log('__init__')
        # initialize all variables
        self.channels = []
        self.Player = MyPlayer()
        self.Player.overlay = self
        self.inputChannel = -1
        self.channelLabel = []
        self.lastActionTime = 0
        self.actionSemaphore = threading.BoundedSemaphore()
        self.channelThread = ChannelListThread()
        self.channelThread.myOverlay = self
        self.timeStarted = 0
        self.infoOnChange = False
        self.infoDuration = 10
        self.infoOffset = 0
        self.invalidatedChannelCount = 0
        self.showingInfo = False
        self.showChannelBug = False
        self.channelBugPosition = 0
        self.notificationLastChannel = 0
        self.notificationLastShow = 0
        self.notificationShowedNotif = False
        self.isExiting = False
        self.maxChannels = 0
        self.notPlayingCount = 0
        self.ignoreInfoAction = False
        self.shortItemLength = 120
        self.seekForward = 30
        self.seekBackward = -30
        self.runningActionChannel = 0
        self.channelDelay = 500
        self.holdActions = 3
        self.channelDisplayTimerCount = 1.0  #reduced from 3.0, can always press I to get it again
        self.playerTimerCount = 3.0
        self.numberColor = '0xFF00FF00'
        self.sleepTimeValue = 0
        self.StartChannel = 1
        self.AlwaysUseStartChannel = False
        self.highestValidChannel = 0
        self.inputValue = []
        self.HideClipsDuringShort = False
        self.ComingUpClipLength = 120
        self.BugBrightness = 2.0
        self.ColorBug = False
        self.HideLeadingZeroes = False
        self.previousChannel = 1
        self.startmode = 1
        self.languageChangeChannel = ""
        self.languageChange = ""
        self.languageChangeChannel2 = ""
        self.languageChange2 = ""

        for i in range(3):
            self.numberColor = NUM_COLOUR[int(ADDON.getSetting("NumberColour"))]
            self.channelLabel.append(xbmcgui.ControlImage(90 + (35 * i), 90, 50, 50, IMAGES_LOC, colorDiffuse=self.numberColor))
            self.addControl(self.channelLabel[i])
            self.channelLabel[i].setVisible(False)

        self.doModal()
        self.log('__init__ return')

    def resetChannelTimes(self):
        for i in range(self.maxChannels):
            self.channels[i].setAccessTime(self.timeStarted - self.channels[i].totalTimePlayed)

    def onFocus(self, controlId):
        pass

    def findValidChannels(self):
        #find channels that are not marked Don't Play
        validChannels = []
        i = 0
        maxChannel = self.maxChannels
        while i < maxChannel:
            if self.channels[i].isValid == True:
                validChannels.append(int(i) + 1)
            i  = i + 1
        #temporarily putting default=0
        highestValidChannel = max(validChannels, default=0)
        return highestValidChannel

    # override the doModal function so we can setup everything first
    def onInit(self):
        self.log('Overlay onInit')

        if FileAccess.exists(GEN_CHAN_LOC) == False:
            try:
                GEN_CHAN_LOC_FIXED = xbmcvfs.translatePath(GEN_CHAN_LOC)
                FileAccess.makedirs(GEN_CHAN_LOC_FIXED)
            except:
                self.Error(LANGUAGE(30035))
                return

        if FileAccess.exists(MADE_CHAN_LOC) == False:
            try:
                
                MADE_CHAN_LOC_FIXED = xbmcvfs.translatePath(GEN_CHAN_LOC)
                FileAccess.makedirs(MADE_CHAN_LOC_FIXED)
            except:
                self.Error(LANGUAGE(30036))
                return

        #translatePath already applied to CHANNELBUG_LOC in Global
        if FileAccess.exists(CHANNELBUG_LOC) == False:
                try:
                    FileAccess.makedirs(CHANNELBUG_LOC)
                except:
                    self.Error(LANGUAGE(30036))
                    return

        self.getControl(102).setVisible(False)
        self.backupFiles()
        ADDON_SETTINGS.loadSettings()

        if CHANNEL_SHARING:
            updateDialog = xbmcgui.DialogProgressBG()
            updateDialog.create(ADDON_NAME, '')
            updateDialog.update(1, message='Initializing Channel Sharing')
            FileAccess.makedirs(LOCK_LOC)
            updateDialog.update(50, message='Initializing Channel Sharing')
            self.isMaster = GlobalFileLock.lockFile("MasterLock", False)
            updateDialog.update(100, message='Initializing Channel Sharing')
            xbmc.sleep(200)
            updateDialog.close()
        else:
            self.isMaster = True

        if self.isMaster:
            migratemaster = Migrate()
            migratemaster.migrate()

        self.channelLabelTimer = threading.Timer(self.channelDisplayTimerCount, self.hideChannelLabel)
        self.playerTimer = threading.Timer(self.playerTimerCount, self.playerTimerAction)
        self.playerTimer.name = "PlayerTimer"
        self.infoTimer = threading.Timer(5.0, self.hideInfo)
        global ROWCOUNT
        self.log('ROWCOUNT Overlay onInit = ' + str(ROWCOUNT))
        self.myEPG = EPGWindow("script.pseudotv.EPG" + str(ROWCOUNT) + ".xml", CWD, "default")
        self.myEPG.MyOverlayWindow = self
        # Don't allow any actions during initialization
        self.actionSemaphore.acquire()
        self.timeStarted = time.time()
        self.inputTimer = threading.Timer(2.0, self.clearInput)

        if self.readConfig() == False:
            return

        self.myEPG.channelLogos = self.channelLogos
        self.maxChannels = len(self.channels)
        log ('self.maxChannels = ' + str(self.maxChannels))

        if self.maxChannels == 0:
            self.Error(LANGUAGE(30037))
            return

        self.highestValidChannel = self.findValidChannels()

        found = False

        for i in range(self.maxChannels):
            if self.channels[i].isValid:
                found = True
                break

        if found == False:
            self.Error(LANGUAGE(30038))
            return

        if self.sleepTimeValue > 0:
            self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

        self.notificationTimer = threading.Timer(NOTIFICATION_CHECK_TIME, self.notificationAction)

        self.log('startup messages begin')
        self.log('AlwaysUseStartChannel = ', str(self.AlwaysUseStartChannel))
        self.log('forceReset = ', str(self.forceReset))
        self.log('channelResetSetting', str(self.channelResetSetting))

        try:
            if self.AlwaysUseStartChannel == True:
                self.log ('start channel should always be based on setting: ', str(self.StartChannel))
                self.currentChannel = self.fixChannel(int(self.StartChannel))
            else:
                if self.forceReset == False and self.channelResetSetting != "5":
                    self.log ('start channel should be last remembered: ', int(ADDON.getSetting("CurrentChannel")))
                    self.currentChannel = self.fixChannel(int(ADDON.getSetting("CurrentChannel")))
                else:
                    self.log ('start channel should be based on setting due to channel reset: ', str(self.StartChannel))
                    self.currentChannel = self.fixChannel(int(self.StartChannel))
        except:
            self.log('error, so defaulting to channel 1')
            self.currentChannel = self.fixChannel(1)

        self.resetChannelTimes()
        self.setFirstChannel(self.currentChannel)
        self.startSleepTimer()
        self.startNotificationTimer()
        self.playerTimer.start()

        if self.backgroundUpdating < 2 or self.isMaster == False:
            self.channelThread.name = "ChannelThread"
            self.channelThread.start()

        self.actionSemaphore.release()
        self.log('onInit return')


    # setup all basic configuration parameters, including creating the playlists that
    # will be used to actually run this thing
    def readConfig(self):
        self.log('readConfig')
        # Sleep setting is in 30 minute incriments...so multiply by 30, and then 60 (min to sec)
        self.sleepTimeValue = int(ADDON.getSetting('AutoOff')) * 1800
        self.log('Auto off is ' + str(self.sleepTimeValue))
        self.infoOnChange = ADDON.getSetting("InfoOnChange") == "true"
        self.infoDuration = INFO_DUR[int(ADDON.getSetting("InfoLength"))]
        self.log('Show info label on channel change is ' + str(self.infoOnChange) + str(self.infoDuration))
        self.showChannelBug = ADDON.getSetting("ShowChannelBug") == "true"
        self.channelBugPosition = CHANNELBUG_POS[int(ADDON.getSetting("ChannelBugPosition"))]
        self.SecondaryBugChannels = ADDON.getSetting('SecondaryBugChannels').split(",")
        self.SecondaryBugPosition = CHANNELBUG_POS[int(ADDON.getSetting("SecondaryBugPosition"))]
        self.log('Show channel bug - ' + str(self.showChannelBug))
        self.forceReset = ADDON.getSetting('ForceChannelReset') == "true"
        self.StartChannel = ADDON.getSetting('StartChannel')
        self.AlwaysUseStartChannel = ADDON.getSetting('AlwaysUseStartChannel') == "true"
        self.channelResetSetting = ADDON.getSetting('ChannelResetSetting')
        self.log("Channel reset setting - " + str(self.channelResetSetting))
        self.channelLogos = xbmcvfs.translatePath(ADDON.getSetting('ChannelLogoFolder'))
        self.backgroundUpdating = int(ADDON.getSetting("ThreadMode"))
        self.log("Background updating - " + str(self.backgroundUpdating))
        self.showNextItem = ADDON.getSetting("EnableComingUp") == "true"
        self.log("Show Next Item - " + str(self.showNextItem))
        self.hideShortItems = ADDON.getSetting("HideClips") == "true"
        self.hideShortItemsEPG = ADDON.getSetting("HideClipsEPG") == "true"
        self.shortItemLength = SHORT_CLIP_ENUM[int(ADDON.getSetting("ClipLength"))]
        self.seekForward = SEEK_FORWARD[int(ADDON.getSetting("SeekForward"))]
        self.seekBackward = SEEK_BACKWARD[int(ADDON.getSetting("SeekBackward"))]
        self.channelDelay = CHANNEL_DELAY[int(ADDON.getSetting("ChannelDelay"))]
        self.holdActions = HOLD_ACTIONS[int(ADDON.getSetting("holdActions"))]
        self.BugBrightness = BUG_BRIGHTNESS[int(ADDON.getSetting("BugBrightness"))]
        self.ColorBug = ADDON.getSetting('ColorBug') == "true"
        self.HideLeadingZeroes = ADDON.getSetting('HideLeadingZeroes') == "true"
        self.StartMode = int(ADDON.getSetting("StartMode"))
        self.languageChangeChannel = ADDON.getSetting('languageChangeChannel').split(",")
        self.languageChange = ADDON.getSetting("languageChange").split(",")
        self.languageChangeChannel2 = ADDON.getSetting('languageChangeChannel2').split(",")
        self.languageChange2 = ADDON.getSetting("languageChange2").split(",")

        if FileAccess.exists(self.channelLogos) == False:
            self.channelLogos = LOGOS_LOC

        self.log('Channel logo folder - ' + self.channelLogos)
        self.channelList = ChannelList()
        self.channelList.myOverlay = self
        self.channels = self.channelList.setupList()

        self.HideClipsDuringShort = ADDON.getSetting('HideClipsDuringShort') == "true"
        self.ComingUpClipLength = int(ADDON.getSetting('ComingUpClipLength'))
        
        if self.channels is None:
            self.log('readConfig No channel list returned')
            self.end()
            return False

        self.Player.stop()
        self.log('readConfig return')
        return True


    # handle fatal errors: log it, show the dialog, and exit
    def Error(self, line1, line2 = '', line3 = ''):
        self.log('FATAL ERROR: ' + line1 + " " + line2 + " " + line3, xbmc.LOGFATAL)
        dlg = xbmcgui.Dialog()
        dlg.ok(xbmc.getLocalizedString(257), line1)
        del dlg
        self.end()


    def channelDown(self):
        self.log('channelDown')

        if self.maxChannels == 1:
            return

        channel = self.fixChannel(self.currentChannel - 1, False)
        self.setChannel(channel)
        self.log('channelDown return')


    def backupFiles(self):
        self.log('backupFiles')

        if CHANNEL_SHARING == False:
            return

        realloc = ADDON.getSetting('SettingsFolder')
        FileAccess.copy(realloc + '/settings2.xml', SETTINGS_LOC + '/settings2.xml')
        realloc = xbmcvfs.translatePath(os.path.join(realloc, 'cache')) + '/'

        for i in range(1000):
            FileAccess.copy(realloc + 'channel_' + str(i) + '.m3u', CHANNELS_LOC + 'channel_' + str(i) + '.m3u')


    def storeFiles(self):
        self.log('storeFiles')

        if CHANNEL_SHARING == False:
            return

        realloc = ADDON.getSetting('SettingsFolder')
        FileAccess.copy(SETTINGS_LOC + '/settings2.xml', realloc + '/settings2.xml')
        realloc = xbmcvfs.translatePath(os.path.join(realloc, 'cache')) + '/'

        for i in range(self.maxChannels + 1):
            FileAccess.copy(CHANNELS_LOC + 'channel_' + str(i) + '.m3u', realloc + 'channel_' + str(i) + '.m3u')


    def channelUp(self):
        self.log('channelUp')

        if self.maxChannels == 1:
            return

        channel = self.fixChannel(self.currentChannel + 1)
        self.setChannel(channel)
        self.log('channelUp return')


    def message(self, data):
        self.log('Dialog message: ' + data)
        dlg = xbmcgui.Dialog()
        dlg.ok(xbmc.getLocalizedString(19033), data)
        del dlg


    def log(self, msg, level = xbmc.LOGDEBUG):
        log('TVOverlay: ' + msg, level)

    def setFirstChannel(self, channel):
        self.log('setFirstChannel ' + str(channel))

        self.lastActionTime = 0
        timedif = 0
        self.showingInfo = False

        self.currentChannel = channel
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        self.log("about to load")

        if xbmc.PlayList(xbmc.PLAYLIST_MUSIC).load(self.channels[channel - 1].fileName) == False:
            self.log("Error loading playlist", xbmc.LOGERROR)
            self.InvalidateChannel(channel)
            return

        curtime = time.time()
        timedif = (curtime - self.channels[self.currentChannel - 1].lastAccessTime)


        # adjust the show and time offsets to properly position inside the playlist
        while self.channels[self.currentChannel - 1].showTimeOffset + timedif > self.channels[self.currentChannel - 1].getCurrentDuration():
            timedif -= self.channels[self.currentChannel - 1].getCurrentDuration() - self.channels[self.currentChannel - 1].showTimeOffset
            self.channels[self.currentChannel - 1].addShowPosition(1)
            self.channels[self.currentChannel - 1].setShowTime(0)

        xbmc.sleep(1000)
        # set the show offset
        self.Player.playselected(self.channels[self.currentChannel - 1].playlistPosition)
        self.log("playing selected file")
        # set the time offset
        self.channels[self.currentChannel - 1].setAccessTime(curtime)

        self.showChannelLabel(self.currentChannel)
        self.lastActionTime = time.time()

        #if self.StartMode == 2:
        #    seektime = self.channels[self.currentChannel - 1].showTimeOffset
        #    self.log('Resume seektime = ' + str(seektime))
        #else:
        #    seektime = self.channels[self.currentChannel - 1].showTimeOffset + timedif
        #    self.log('Realtime seektime = ' + str(seektime))

        seektime = self.channels[self.currentChannel - 1].showTimeOffset + timedif + int((time.time() - curtime))
        try:
            self.Player.seekTime(seektime)
        except:
            self.log('Overlay setFirstChannel - no video playing')


    def setChannel(self, channel):
        self.log('setChannel ' + str(channel))
        self.runActions(RULES_ACTION_OVERLAY_SET_CHANNEL, channel, self.channels[channel - 1])

        if self.Player.stopped:
            self.log('setChannel player already stopped', xbmc.LOGERROR)
            return

        if channel < 1 or channel > self.maxChannels:
            self.log('setChannel invalid channel ' + str(channel), xbmc.LOGERROR)
            return

        if self.channels[channel - 1].isValid == False:
            self.log('setChannel channel not valid ' + str(channel), xbmc.LOGERROR)
            return

        self.lastActionTime = 0
        timedif = 0
        self.getControl(102).setVisible(False)
        self.getControl(103).setImage('')
        self.showingInfo = False

        # first of all, save playing state, time, and playlist offset for
        # the currently playing channel
        if self.Player.isPlaying():
            if channel != self.currentChannel:
                self.channels[self.currentChannel - 1].setPaused(xbmc.getCondVisibility('Player.Paused'))

                # Automatically pause in serial mode
                if self.channels[self.currentChannel - 1].mode & MODE_ALWAYSPAUSE > 0:
                    self.channels[self.currentChannel - 1].setPaused(True)

                self.channels[self.currentChannel - 1].setShowTime(self.Player.getTime())
                self.channels[self.currentChannel - 1].setShowPosition(xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition())
                self.channels[self.currentChannel - 1].setAccessTime(time.time())

            if (str(self.currentChannel) in self.languageChangeChannel) and (len(self.languageChange) == 2):
               self.log('changing back audio for channel = ' + str(self.currentChannel)) 
               self.changeAudio(self.languageChange[1])
            elif (str(self.currentChannel) in self.languageChangeChannel2) and (len(self.languageChange2) == 2):
               self.log('changing back audio for channel = ' + str(self.currentChannel)) 
               self.changeAudio(self.languageChange2[1])

        self.previousChannel = self.currentChannel
        self.currentChannel = channel
        # now load the proper channel playlist
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        self.log("about to load")

        if xbmc.PlayList(xbmc.PLAYLIST_MUSIC).load(self.channels[channel - 1].fileName) == False:
            self.log("Error loading playlist", xbmc.LOGERROR)
            self.InvalidateChannel(channel)
            return

        # Disable auto playlist shuffling if it's on
        if xbmc.getInfoLabel('Playlist.Random').lower() == 'random':
            self.log('Random on.  Disabling.')
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).unshuffle()

        self.log("repeat all")
        xbmc.executebuiltin("PlayerControl(RepeatAll)")
        curtime = time.time()
        timedif = (curtime - self.channels[self.currentChannel - 1].lastAccessTime)

        if self.channels[self.currentChannel - 1].isPaused == False:
            # adjust the show and time offsets to properly position inside the playlist
            while self.channels[self.currentChannel - 1].showTimeOffset + timedif > self.channels[self.currentChannel - 1].getCurrentDuration():
                timedif -= self.channels[self.currentChannel - 1].getCurrentDuration() - self.channels[self.currentChannel - 1].showTimeOffset
                self.channels[self.currentChannel - 1].addShowPosition(1)
                self.channels[self.currentChannel - 1].setShowTime(0)

        

        xbmc.sleep(self.channelDelay)
        # set the show offset
        self.Player.playselected(self.channels[self.currentChannel - 1].playlistPosition)
        self.log("playing selected file")
        # set the time offset
        self.channels[self.currentChannel - 1].setAccessTime(curtime)
        
        if self.channels[self.currentChannel - 1].isPaused:
            self.channels[self.currentChannel - 1].setPaused(False)
            self.log('The seek bit - paused')
            try:
                self.Player.seekTime(self.channels[self.currentChannel - 1].showTimeOffset)

                if self.channels[self.currentChannel - 1].mode & MODE_ALWAYSPAUSE == 0:
                    self.Player.pause()

                    if self.waitForVideoPaused() == False:
                        return
            except:
                self.log('Exception during seek on paused channel', xbmc.LOGERROR)
        else:
            self.log('The seek bit - not paused')
            seektime = self.channels[self.currentChannel - 1].showTimeOffset + timedif + int((time.time() - curtime))

            try:
                self.log("Seeking")
                self.Player.seekTime(seektime)
            except:
                self.log("Exception Unable to set proper seek time, trying different value")

                try:
                    seektime = self.channels[self.currentChannel - 1].showTimeOffset + timedif
                    self.Player.seekTime(seektime)
                except:
                    self.log('Exception during seek', xbmc.LOGERROR)

        if str(channel) in self.languageChangeChannel:
            self.log('changing audio for channel = ' + str(channel))
            self.changeAudio(self.languageChange[0])
        elif str(channel) in self.languageChangeChannel2:
            self.log('changing audio for channel = ' + str(channel))
            self.changeAudio(self.languageChange2[0])
        
        self.showChannelLabel(self.currentChannel)
        
        self.lastActionTime = time.time()
        self.runActions(RULES_ACTION_OVERLAY_SET_CHANNEL_END, channel, self.channels[channel - 1])
        self.log('setChannel return')

    def changeAudio(self,language):
        availAudio = self.Player.getAvailableAudioStreams()
        track = -1
        self.log('self.currentChannel = ' + str(self.currentChannel))
        self.log('language = ' + str(language))
        self.log('availAudio = ' + str(availAudio))

        if language in availAudio:
            i = 0
            for stream in availAudio:
                self.log('stream = ' + str(stream))
                if language in stream:
                    self.log('audio match')
                    track = i
                    break
                i += 1

        if track != -1:
            xbmc.Player().setAudioStream(track)

    def InvalidateChannel(self, channel):
        self.log("InvalidateChannel" + str(channel))

        if channel < 1 or channel > self.maxChannels:
            self.log("InvalidateChannel invalid channel " + str(channel))
            return

        self.channels[channel - 1].isValid = False
        self.invalidatedChannelCount += 1

        if self.invalidatedChannelCount > 3:
            self.Error(LANGUAGE(30039))
            return

        remaining = 0

        for i in range(self.maxChannels):
            if self.channels[i].isValid:
                remaining += 1

        if remaining == 0:
            self.Error(LANGUAGE(30040))
            return

        self.setChannel(self.fixChannel(channel))


    def waitForVideoPaused(self):
        self.log('waitForVideoPaused')
        sleeptime = 0

        while sleeptime < TIMEOUT:
            xbmc.sleep(100)

            if self.Player.isPlaying():
                if xbmc.getCondVisibility('Player.Paused'):
                    break

            sleeptime += 100
        else:
            self.log('Timeout waiting for pause', xbmc.LOGERROR)
            return False

        self.log('waitForVideoPaused return')
        return True

    def setShowInfo(self):
        self.log('setShowInfo')

        if self.infoOffset > 0:
            #Coming Up
            self.getControl(502).setLabel(LANGUAGE(30041))
        elif self.infoOffset < 0:
            #Already Seen
            self.getControl(502).setLabel(LANGUAGE(30042))
        elif self.infoOffset == 0:
            #Now Playing
            self.getControl(502).setLabel(LANGUAGE(30043))

        if self.hideShortItems and self.infoOffset != 0:
            position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
            curoffset = 0
            modifier = 1

            if self.infoOffset < 0:
                modifier = -1

            while curoffset != abs(self.infoOffset):
                position = self.channels[self.currentChannel - 1].fixPlaylistIndex(position + modifier)

                if self.channels[self.currentChannel - 1].getItemDuration(position) >= self.shortItemLength:
                    curoffset += 1
        else:
            position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition() + self.infoOffset

        self.getControl(503).setLabel(self.channels[self.currentChannel - 1].getItemTitle(position))
        self.getControl(504).setLabel(self.channels[self.currentChannel - 1].getItemEpisodeTitle(position))
        self.getControl(505).setText(self.channels[self.currentChannel - 1].getItemDescription(position))
        self.getControl(506).setImage(self.channelLogos + ascii(self.channels[self.currentChannel - 1].name) + '.png')
        if not FileAccess.exists(self.channelLogos + ascii(self.channels[self.currentChannel - 1].name) + '.png'):
            self.getControl(506).setImage(IMAGES_LOC + 'Default.png')

        self.log('setShowInfo return')


    # Display the current channel based on self.currentChannel.
    # Start the timer to hide it.
    def showChannelLabel(self, channel):
        self.log('showChannelLabel ' + str(channel))

        if self.channelLabelTimer.is_alive():
            self.channelLabelTimer.cancel()
            self.channelLabelTimer = threading.Timer(self.channelDisplayTimerCount, self.hideChannelLabel)

        tmp = self.inputChannel
        self.hideChannelLabel()
        self.inputChannel = tmp
        channelString = str(channel)
        if self.highestValidChannel < 10:
            self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString + '.png')
            self.channelLabel[0].setVisible(True)
        elif self.highestValidChannel < 100:
            if len(channelString) == 1:
                if self.HideLeadingZeroes:
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                else:
                    channelString = '0' + channelString
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                    self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                    self.channelLabel[1].setVisible(True)
            else:
                self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                self.channelLabel[0].setVisible(True)
                self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                self.channelLabel[1].setVisible(True)
        else:
            if len(channelString) == 1:
                if self.HideLeadingZeroes:
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                else:
                    channelString = '0' + '0' + channelString
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                    self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                    self.channelLabel[1].setVisible(True)
                    self.channelLabel[2].setImage(IMAGES_LOC + 'label_' + channelString[2] + '.png')
                    self.channelLabel[2].setVisible(True)
            elif len(channelString) == 2:
                if self.HideLeadingZeroes:
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                    self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                    self.channelLabel[1].setVisible(True)
                else:
                    channelString = '0' + channelString
                    self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                    self.channelLabel[0].setVisible(True)
                    self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                    self.channelLabel[1].setVisible(True)
                    self.channelLabel[2].setImage(IMAGES_LOC + 'label_' + channelString[2] + '.png')
                    self.channelLabel[2].setVisible(True)
            else:
                self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
                self.channelLabel[0].setVisible(True)
                self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
                self.channelLabel[1].setVisible(True)
                self.channelLabel[2].setImage(IMAGES_LOC + 'label_' + channelString[2] + '.png')
                self.channelLabel[2].setVisible(True)

        if self.inputChannel == -1 and self.infoOnChange == True:
            self.infoOffset = 0
            xbmc.sleep(self.channelDelay)
            self.showInfo(self.infoDuration)

        self.setChannelBug(channel)

        if xbmc.getCondVisibility('Player.ShowInfo'):
            json_query = '{"jsonrpc": "2.0", "method": "Input.Info", "id": 1}'
            self.ignoreInfoAction = True
            self.channelList.sendJSON(json_query)
        self.channelLabelTimer.name = "ChannelLabel"
        self.channelLabelTimer.start()
        self.startNotificationTimer()
        self.log('showChannelLabel return')

    def showInputLabel(self, channelString):
        self.log('showInputLabel ' + channelString)

        if self.channelLabelTimer.is_alive():
            self.channelLabelTimer.cancel()
            self.channelLabelTimer = threading.Timer(self.channelDisplayTimerCount, self.hideChannelLabel)

        tmp = self.inputChannel
        self.hideChannelLabel()
        self.inputChannel = tmp

        if len(channelString) == 1:
            self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
            self.channelLabel[0].setVisible(True)
        if len(channelString) == 2:
            self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
            self.channelLabel[0].setVisible(True)
            self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
            self.channelLabel[1].setVisible(True)
        if len(channelString) == 3:
            self.channelLabel[0].setImage(IMAGES_LOC + 'label_' + channelString[0] + '.png')
            self.channelLabel[0].setVisible(True)
            self.channelLabel[1].setImage(IMAGES_LOC + 'label_' + channelString[1] + '.png')
            self.channelLabel[1].setVisible(True)
            self.channelLabel[2].setImage(IMAGES_LOC + 'label_' + channelString[2] + '.png')
            self.channelLabel[2].setVisible(True)
        self.channelLabelTimer.name = "ChannelLabel"
        self.channelLabelTimer.start()
        self.startNotificationTimer()

    def setChannelBug(self, channel):
        
        self.log('Channel: ' + str(channel) + ' SecondaryBugChannels: ' + str(self.SecondaryBugChannels))
        
        if str(channel) in self.SecondaryBugChannels:
            self.log('Secondary channels found')
            posx = self.SecondaryBugPosition[0]
            posy = self.SecondaryBugPosition[1]
        else:   
            self.log('Secondary channels NOT found')
            posx = self.channelBugPosition[0]
            posy = self.channelBugPosition[1]

        if self.showChannelBug:
            try:
                if not FileAccess.exists(self.channelLogos + ascii(self.channels[self.currentChannel - 1].name) + '.png'):
                    self.getControl(103).setImage(IMAGES_LOC + 'Default2.png')
                    self.getControl(103).setPosition(posx, posy)
                original = Image.open(self.channelLogos + ascii(self.channels[self.currentChannel - 1].name) + '.png')

                if self.ColorBug:
                    converted_img =  original.convert('RGBA')
                else:
                    converted_img = original.convert('LA')

                img_bright = ImageEnhance.Brightness(converted_img)
                converted_img = img_bright.enhance(self.BugBrightness)

                if not FileAccess.exists(CHANNELBUG_LOC + ascii(self.channels[self.currentChannel - 1].name) + '.png'):
                    converted_img.save(CHANNELBUG_LOC + ascii(self.channels[self.currentChannel - 1].name) + '.png')
                self.getControl(103).setImage(CHANNELBUG_LOC + ascii(self.channels[self.currentChannel - 1].name) + '.png')
                self.getControl(103).setPosition(posx, posy)

            except:
               if not FileAccess.exists(CHANNELBUG_LOC + ascii(self.channels[self.currentChannel - 1].name) + '.png'):
                    self.getControl(103).setImage(IMAGES_LOC + 'Default2.png')
               else:
                    self.getControl(103).setImage(CHANNELBUG_LOC + ascii(self.channels[self.currentChannel - 1].name) + '.png')
               self.getControl(103).setPosition(posx, posy)
        else:
            self.getControl(103).setImage('')


    # Called from the timer to hide the channel label.
    def hideChannelLabel(self):
        self.log('hideChannelLabel')
        self.channelLabelTimer = threading.Timer(self.channelDisplayTimerCount, self.hideChannelLabel)

        for i in range(3):
            self.channelLabel[i].setVisible(False)

        self.inputChannel = -1
        self.log('hideChannelLabel return')

    def hideInfo(self):
        self.getControl(102).setVisible(False)
        self.getControl(103).setVisible(True)
        self.infoOffset = 0
        self.showingInfo = False

        if self.infoTimer.is_alive():
            self.infoTimer.cancel()
        self.hideChannelLabel()
        self.infoTimer = threading.Timer(5.0, self.hideInfo)

    def clearInput(self):
        self.inputValue = []


    def showInfo(self, timer):
        if self.hideShortItemsEPG:
            position = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition() + self.infoOffset

            if self.channels[self.currentChannel - 1].getItemDuration(xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()) < self.shortItemLength:
                return

        self.getControl(103).setVisible(False)
        self.getControl(102).setVisible(True)
        self.showingInfo = True
        self.setShowInfo()

        if self.infoTimer.is_alive():
            self.infoTimer.cancel()

        self.infoTimer = threading.Timer(timer, self.hideInfo)
        self.infoTimer.name = "InfoTimer"

        #This surpresses the PSTV info screen if the Kodi info screen is showing.  Better to hide the Kodi screen via your skin.
        #if xbmc.getCondVisibility('Player.ShowInfo'):
        #    json_query = '{"jsonrpc": "2.0", "method": "Input.Info", "id": 1}'
        #    self.ignoreInfoAction = True
        #    self.channelList.sendJSON(json_query)

        self.infoTimer.start()


    # return a valid channel in the proper range
    def fixChannel(self, channel, increasing = True):
        while channel < 1 or channel > self.maxChannels:
            if channel < 1: channel = self.maxChannels + channel
            if channel > self.maxChannels: channel -= self.maxChannels

        if increasing:
            direction = 1
        else:
            direction = -1

        if self.channels[channel - 1].isValid == False:
            return self.fixChannel(channel + direction, increasing)

        return channel

    # Handle all input while videos are playing
    def onAction(self, act):
        action = act.getId()
        self.log('onAction ' + str(action))

        if self.Player.stopped:
            return

        # Since onAction isnt always called from the same thread (weird),
        # ignore all actions if we're in the middle of processing one
        if self.actionSemaphore.acquire(False) == False:
            self.log('Unable to get semaphore')
            return

        lastaction = time.time() - self.lastActionTime

        # during certain times we just want to discard all input
        if lastaction < self.holdActions:
            self.log('Not allowing actions')
            action = ACTION_INVALID

        self.startSleepTimer()

        if action == ACTION_SELECT_ITEM:
            # If we're manually typing the channel, set it now
            if self.inputChannel > 0:
                if self.inputChannel != self.currentChannel and self.inputChannel <= self.maxChannels:
                    self.setChannel(self.inputChannel)
                    if self.infoOnChange == True:
                        self.infoOffset = 0
                        xbmc.sleep(self.channelDelay)
                        self.showInfo(self.infoDuration)
                self.inputChannel = -1
            else:
                # Otherwise, show the EPG
                if self.channelThread.is_alive():
                    self.channelThread.pause()

                if self.notificationTimer.is_alive():
                    self.notificationTimer.cancel()
                    self.notificationTimer = threading.Timer(NOTIFICATION_CHECK_TIME, self.notificationAction)

                if self.sleepTimeValue > 0:
                    if self.sleepTimer.is_alive():
                        self.sleepTimer.cancel()
                        self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

                self.hideInfo()
                #self.getControl(103).setVisible(False)
                self.newChannel = 0
                global ROWCOUNT
                self.log('ROWCOUNT Overlay onAction= ' + str(ROWCOUNT))
                self.myEPG.doModal()
                self.getControl(103).setVisible(True)

                if self.channelThread.is_alive():
                    self.channelThread.unpause()

                self.startNotificationTimer()

                if self.newChannel != 0:
                    self.setChannel(self.newChannel)

        elif action == ACTION_MOVE_UP or action == ACTION_PAGEUP:
            self.channelUp()
        elif action == ACTION_MOVE_DOWN or action == ACTION_PAGEDOWN:
            self.channelDown()
        elif action == ACTION_MOVE_LEFT:
            if self.showingInfo:
                self.infoOffset -= 1
                self.showInfo(10)
            else:
                xbmc.executebuiltin("Seek("+str(self.seekBackward)+")")

        elif action == ACTION_MOVE_RIGHT:
            if self.showingInfo:
                self.infoOffset += 1
                self.showInfo(10)
            else:
                xbmc.executebuiltin("Seek("+str(self.seekForward)+")")

        elif action in ACTION_PREVIOUS_MENU:
            if self.showingInfo:
                self.hideInfo()
            else:
                dlg = xbmcgui.Dialog()

                if self.sleepTimeValue > 0:
                    if self.sleepTimer.is_alive():
                        self.sleepTimer.cancel()
                        self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

                if dlg.yesno(xbmc.getLocalizedString(13012), LANGUAGE(30031)):
                    self.end()
                    return  # Don't release the semaphore
                else:
                    self.startSleepTimer()

        elif action == ACTION_SHOW_INFO:
            if self.ignoreInfoAction:
                self.ignoreInfoAction = False
            else:
                if self.showingInfo:
                    self.hideInfo()
                    if xbmc.getCondVisibility('Player.ShowInfo'):
                        json_query = '{"jsonrpc": "2.0", "method": "Input.Info", "id": 1}'
                        self.ignoreInfoAction = True
                        self.channelList.sendJSON(json_query)
                else:
                    self.showInfo(10)
                    self.showChannelLabel(self.currentChannel)
        elif action >= ACTION_NUMBER_0 and action <= ACTION_NUMBER_9:
            if self.inputTimer.is_alive():
                self.inputTimer.cancel()
            self.inputTimer = threading.Timer(1, self.clearInput)
            self.inputTimer.start()
            channelInput = action - ACTION_NUMBER_0
            self.inputValue.append(channelInput)
            channelString = str1 = ''.join(str(e) for e in self.inputValue)
            self.log('channelString = ' + channelString)
            self.showInputLabel(channelString)
            if self.highestValidChannel < 100:
                maxDigits = 2
            else:
                maxDigits = 3
            if len(channelString) == maxDigits:
                self.clearInput()
                channelCandidate = int(channelString)
                if channelCandidate != self.currentChannel and channelCandidate <= self.highestValidChannel:
                            self.setChannel(channelCandidate)
        elif action == ACTION_OSD:
            xbmc.executebuiltin("ActivateWindow(videoosd)")
        elif action == ACTION_PREV_PICTURE:
            self.setChannel(self.previousChannel)

        self.actionSemaphore.release()
        self.log('onAction return')


    # Reset the sleep timer
    def startSleepTimer(self):
        if self.sleepTimeValue == 0:
            return

        # Cancel the timer if it is still running
        if self.sleepTimer.is_alive():
            self.sleepTimer.cancel()
            self.sleepTimer = threading.Timer(self.sleepTimeValue, self.sleepAction)

        if self.Player.stopped == False:
            self.sleepTimer.name = "SleepTimer"
            self.sleepTimer.start()


    def startNotificationTimer(self, timertime = NOTIFICATION_CHECK_TIME):
        self.log("startNotificationTimer")

        if self.notificationTimer.is_alive():
            self.notificationTimer.cancel()

        self.notificationTimer = threading.Timer(timertime, self.notificationAction)

        if self.Player.stopped == False:
            self.notificationTimer.name = "NotificationTimer"
            self.notificationTimer.start()


    # This is called when the sleep timer expires
    def sleepAction(self):
        self.log("sleepAction")
        self.actionSemaphore.acquire()
        self.end()


    # Run rules for a channel
    def runActions(self, action, channel, parameter):
        self.log("runActions " + str(action) + " on channel " + str(channel))

        if channel < 1:
            return

        self.runningActionChannel = channel
        index = 0

        for rule in self.channels[channel - 1].ruleList:
            if rule.actions & action > 0:
                self.runningActionId = index
                parameter = rule.runAction(action, self, parameter)

            index += 1

        self.runningActionChannel = 0
        self.runningActionId = 0
        return parameter


    def notificationAction(self):
        self.log("notificationAction")
        docheck = False

        if self.showNextItem == False:
            return

        if self.Player.isPlaying():
            if self.notificationLastChannel != self.currentChannel:
                docheck = True
            else:
                if self.notificationLastShow != xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition():
                    docheck = True
                else:
                    if self.notificationShowedNotif == False:
                        docheck = True

            if docheck == True:
                self.notificationLastChannel = self.currentChannel
                self.notificationLastShow = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
                self.notificationShowedNotif = False

                #Don't show any notification if the CURRENT show is short
                if self.HideClipsDuringShort:
                    if self.channels[self.currentChannel - 1].getItemDuration(self.notificationLastShow) < self.ComingUpClipLength:
                            self.notificationShowedNotif = True

                timedif = self.channels[self.currentChannel - 1].getItemDuration(self.notificationLastShow) - self.Player.getTime()

                if self.notificationShowedNotif == False and timedif < NOTIFICATION_TIME_BEFORE_END and timedif > NOTIFICATION_DISPLAY_TIME:
                    nextshow = self.channels[self.currentChannel - 1].fixPlaylistIndex(self.notificationLastShow + 1)

                    if self.hideShortItems:
                        # Don't show notification if the NEXT show is short  Instead find the first upcoming show that is not short
                        while nextshow != self.notificationLastShow:
                            if self.channels[self.currentChannel - 1].getItemDuration(nextshow) >= self.shortItemLength:
                                break

                            nextshow = self.channels[self.currentChannel - 1].fixPlaylistIndex(nextshow + 1)

                    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (LANGUAGE(30005), self.channels[self.currentChannel - 1].getItemTitle(nextshow).replace(',', ''), NOTIFICATION_DISPLAY_TIME * 1000, ICON))
                    self.notificationShowedNotif = True

        self.startNotificationTimer()


    def playerTimerAction(self):
        self.playerTimer = threading.Timer(self.playerTimerCount, self.playerTimerAction)
        if self.Player.isPlaying():
            self.lastPlayTime = int(self.Player.getTime())
            self.lastPlaylistPosition = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
            self.notPlayingCount = 0
        else:
            xbmc.sleep(200)
            if self.Player.isPlaying():
                self.lastPlayTime = int(self.Player.getTime())
                self.lastPlaylistPosition = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
                self.notPlayingCount = 0
            else:
                self.notPlayingCount += 1
                self.log("Adding to notPlayingCount")

        if self.notPlayingCount >= 3:
            self.end()
            return

        if self.Player.stopped == False:
            self.playerTimer.name = "PlayerTimer"
            self.playerTimer.start()


    # cleanup and end
    def end(self):
        self.log('end')
        # Prevent the player from setting the sleep timer
        self.Player.stopped = True
        curtime = time.time()
        self.isExiting = True
        updateDialog = xbmcgui.DialogProgressBG()
        updateDialog.create(ADDON_NAME, '')

        if self.isMaster and CHANNEL_SHARING == True:
            updateDialog.update(1, message='Exiting - Removing File Locks')
            GlobalFileLock.unlockFile('MasterLock')

        GlobalFileLock.close()

        if self.playerTimer.is_alive():
            self.playerTimer.cancel()
            self.playerTimer.join()

        if self.Player.isPlaying():
            self.lastPlayTime = self.Player.getTime()
            self.lastPlaylistPosition = xbmc.PlayList(xbmc.PLAYLIST_MUSIC).getposition()
            self.Player.stop()

        updateDialog.update(2, message='Exiting - Stopping Threads')

        try:
            if self.channelLabelTimer.is_alive():
                self.channelLabelTimer.cancel()
                self.channelLabelTimer.join()
        except:
            pass

        updateDialog.update(3, message='Exiting - Stopping Threads')

        try:
            if self.notificationTimer.is_alive():
                self.notificationTimer.cancel()
                self.notificationTimer.join()
        except:
            pass

        updateDialog.update(4, message='Exiting - Stopping Threads')

        try:
            if self.infoTimer.is_alive():
                self.infoTimer.cancel()
                self.infoTimer.join()
        except:
            pass

        updateDialog.update(5, message='Exiting - Stopping Threads')

        try:
            if self.sleepTimeValue > 0:
                if self.sleepTimer.is_alive():
                    self.sleepTimer.cancel()
        except:
            pass

        updateDialog.update(6, message='Exiting - Stopping Threads')

        if self.channelThread.is_alive():
            for i in range(30):
                try:
                    self.channelThread.join(1.0)
                except:
                    pass

                if self.channelThread.is_alive() == False:
                    break

                updateDialog.update(6 + i, message='Exiting - Stopping Threads')

            if self.channelThread.is_alive():
                self.log("Problem joining channel thread", xbmc.LOGERROR)

        if self.isMaster:
            try:
                ADDON.setSetting('CurrentChannel', str(self.currentChannel))
            except:
                pass

            ADDON_SETTINGS.setSetting('LastExitTime', str(int(curtime)))

        if self.timeStarted > 0 and self.isMaster:
            updateDialog.update(35, message='Exiting - Saving Settings')
            validcount = 0

            for i in range(self.maxChannels):
                if self.channels[i].isValid:
                    validcount += 1

            if validcount > 0:
                incval = 65.0 / float(validcount)

                for i in range(self.maxChannels):
                    updateDialog.update(35 + int((incval * i)))

                    if self.channels[i].isValid:
                        if self.channels[i].mode & MODE_RESUME == 0:
                            ADDON_SETTINGS.setSetting('Channel_' + str(i + 1) + '_time', str(int(curtime - self.timeStarted + self.channels[i].totalTimePlayed)))
                        else:
                            if i == self.currentChannel - 1:
                                # Determine pltime...the time it at the current playlist position
                                pltime = 0
                                self.log("position for current playlist is " + str(self.lastPlaylistPosition))

                                for pos in range(self.lastPlaylistPosition):
                                    pltime += self.channels[i].getItemDuration(pos)

                                ADDON_SETTINGS.setSetting('Channel_' + str(i + 1) + '_time', str(pltime + self.lastPlayTime))
                            else:
                                tottime = 0

                                for j in range(self.channels[i].playlistPosition):
                                    tottime += self.channels[i].getItemDuration(j)

                                tottime += self.channels[i].showTimeOffset
                                ADDON_SETTINGS.setSetting('Channel_' + str(i + 1) + '_time', str(int(tottime)))

                self.storeFiles()

        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
        xbmc.executebuiltin("PlayerControl(RepeatOff)")
        updateDialog.close()

        if ADDON.getSettingBool("ResetWatched"):
            Reset = ResetWatched()
            self.log("PSTV Watched List: " + str(self.Player.watchedList), xbmc.LOGWARNING)
            Reset.Resetter(self.Player.watchedList)

        self.close()
