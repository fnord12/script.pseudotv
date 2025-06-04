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

# Channel Types
# 0 - playlist, # 1 - tv network, # 2 - movie studio, # 3 - tv genre
# 4 - movie genre, 5 - mixed genre, # 6 - single show, # 7 - directory

import xbmc, xbmcgui, xbmcaddon, xbmcvfs
import subprocess, os
import time, threading
import datetime
import sys, re
import random


ADDON       = xbmcaddon.Addon(id='script.pseudotv')
CWD         = ADDON.getAddonInfo('path')
RESOURCE    = xbmcvfs.translatePath(os.path.join(CWD, 'resources', 'lib').encode("utf-8"))

sys.path.append(RESOURCE)

SkinID = xbmc.getSkinDir()
if SkinID != 'skin.estuary':
    import MyFont
    if MyFont.getSkinRes() == '1080i':
        MyFont.addFont("PseudoTv10", "NotoSans-Regular.ttf", "23")
        MyFont.addFont("PseudoTv12", "NotoSans-Regular.ttf", "25")
        MyFont.addFont("PseudoTv13", "NotoSans-Regular.ttf", "30")
        MyFont.addFont("PseudoTv14", "NotoSans-Regular.ttf", "32")
    else:
        MyFont.addFont("PseudoTv10", "NotoSans-Regular.ttf", "14")
        MyFont.addFont("PseudoTv12", "NotoSans-Regular.ttf", "16")
        MyFont.addFont("PseudoTv13", "NotoSans-Regular.ttf", "20")
        MyFont.addFont("PseudoTv14", "NotoSans-Regular.ttf", "22")

from xml.dom.minidom import parse, parseString
from Globals import *
from ChannelList import ChannelList
from AdvancedConfig import AdvancedConfig
from FileAccess import FileAccess
from Migrate import Migrate
from contextlib import contextmanager

NUMBER_CHANNEL_TYPES = 8

@contextmanager
def busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialognocancel)')
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close(busydialognocancel)')

class ConfigWindow(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        self.log("__init__")
        xbmcgui.WindowXMLDialog.__init__(self, *args, **kwargs)
        self.madeChanges = 0
        self.showingList = True
        self.channel = 0
        self.channel_type = 9999
        self.setting1 = ''
        self.setting2 = ''
        self.setting3 = ''
        self.savedRules = False
        self.maxNeededChannels = int(ADDON.getSetting("maxNeededChannels"))*50 + 100

        if CHANNEL_SHARING:
            realloc = ADDON.getSetting('SettingsFolder')
            FileAccess.copy(realloc + '/settings2.xml', SETTINGS_LOC + '/settings2.xml')

        ADDON_SETTINGS.loadSettings()
        ADDON_SETTINGS.disableWriteOnSave()
        
        self.initToggles()
        
        self.doModal()
        self.log("__init__ return")


    def log(self, msg, level = xbmc.LOGDEBUG):
        log('ChannelConfig: ' + msg, level)


    def onInit(self):
        self.log("onInit")

        for i in range(NUMBER_CHANNEL_TYPES):
            try:
                self.getControl(120 + i).setVisible(False)
            except:
                pass

        migratemaster = Migrate()
        migratemaster.migrate()
        with busy_dialog():
            self.prepareConfig()
        self.myRules = AdvancedConfig("script.pseudotv.AdvancedConfig.xml", CWD, "default")
        self.log("onInit return")

    def initToggles(self):
        self.altcolorchannels1 = ADDON.getSetting('altcolorchannels1').split(",")
        self.altcolorchannels2 = ADDON.getSetting('altcolorchannels2').split(",")
        self.altcolorchannels3 = ADDON.getSetting('altcolorchannels3').split(",")
        self.languageChangeChannel = ADDON.getSetting('languageChangeChannel').split(",")
        self.languageChangeChannel2 = ADDON.getSetting('languageChangeChannel2').split(",")
        self.UseEpisodeTitleHideTitle = ADDON.getSetting('UseEpisodeTitleHideTitle').split(",")
        self.UseEpisodeTitleKeepShowTitle = ADDON.getSetting('UseEpisodeTitleKeepShowTitle').split(",")
        self.HideDirectoryTitle = ADDON.getSetting('HideDirectoryTitle').split(",")
        self.longBlockChannel = ADDON.getSetting('longBlockChannel').split(",")
        self.ExcludeFromReset = ADDON.getSetting('ExcludeFromReset').split(",")
        self.SecondaryBugChannels = ADDON.getSetting('SecondaryBugChannels').split(",")

        self.toggles = [
            ["altcolorchannels1", self.altcolorchannels1], 
            ["altcolorchannels2", self.altcolorchannels2],
            ["altcolorchannels3", self.altcolorchannels3],
            ["languageChangeChannel", self.languageChangeChannel],
            ["languageChangeChannel2", self.languageChangeChannel2],
            ["UseEpisodeTitleHideTitle", self.UseEpisodeTitleHideTitle],
            ["UseEpisodeTitleKeepShowTitle", self.UseEpisodeTitleKeepShowTitle], 
            ["HideDirectoryTitle", self.HideDirectoryTitle], 
            ["longBlockChannel", self.longBlockChannel],
            ["ExcludeFromReset", self.ExcludeFromReset],
            ["SecondaryBugChannels", self.SecondaryBugChannels]
        ]
        
        self.toggleLen = len(self.toggles)
        
        self.log ('TGGLE init self.toggles: ' + str(self.toggles))
    
    
    def onFocus(self, controlId):
        pass


    def onAction(self, act):
        action = act.getId()

        if action in ACTION_PREVIOUS_MENU:
            if self.showingList == False:
                self.cancelChan()
                self.hideChanDetails()
            else:
                if self.madeChanges == 1:
                    dlg = xbmcgui.Dialog()

                    if dlg.yesno(xbmc.getLocalizedString(190), LANGUAGE(30032)):
                        ADDON_SETTINGS.writeSettings()
                        self.writeToggleSetting()

                        if CHANNEL_SHARING:
                            realloc = ADDON.getSetting('SettingsFolder')
                            FileAccess.copy(SETTINGS_LOC + '/settings2.xml', realloc + '/settings2.xml')
                self.close()
        elif action == CONTEXT_MENU:
            curchan = self.listcontrol.getSelectedPosition() + 1
            AffectChannelOptions = ("Copy Channel", "Swap Channels", "Insert Channel (and move down)", "Delete Channel (and move up)", "Clear Channel")
            ChannelAction = xbmcgui.Dialog().select("Choose An Action For Channel %d" % curchan,AffectChannelOptions)
            if ChannelAction != -1:
                if ChannelAction == 0:
                    result = (xbmcgui.Dialog().numeric(0,"Copy To (and overwrite) Channel"))
                    if result:
                        CopyToChannel = int(result)
                        if 1 <= CopyToChannel <= self.maxNeededChannels:
                            self.copyChannel(curchan,CopyToChannel)
                        else:
                            dialog = xbmcgui.Dialog()
                            ok = dialog.ok('PseudoTV Config','Channel out of range.')
                elif ChannelAction == 1:
                    result = (xbmcgui.Dialog().numeric(0,"Swap Channel %d with Channel:" % curchan))
                    if result:
                        SwapToChannel = int(result)
                        if 1 <= SwapToChannel <= self.maxNeededChannels:
                            firstEmpty = self.findFirstEmpty(curchan)
                            self.swapChannel(curchan,SwapToChannel,firstEmpty)
                        else:
                            dialog = xbmcgui.Dialog()
                            ok = dialog.ok('PseudoTV Config','Channel out of range.')
                elif ChannelAction == 2:
                    firstEmpty = self.findFirstEmpty(curchan)
                    self.insertChannel(curchan,firstEmpty)
                elif ChannelAction == 3:
                    firstEmpty = self.findFirstEmpty(curchan)
                    self.deleteChannel(curchan,firstEmpty)
                elif ChannelAction == 4:
                    self.clearChannel(curchan)
        elif act.getButtonCode() == 61575:      # Delete button
            curchan = self.listcontrol.getSelectedPosition() + 1
            self.clearChannel(curchan)

    def saveSettings(self):
        self.log("saveSettings channel " + str(self.channel))
        chantype = 9999
        chan = str(self.channel)
        set1 = ''
        set2 = ''

        try:
            chantype = int(ADDON_SETTINGS.getSetting("Channel_" + chan + "_type"))
        except:
            self.log("Unable to get channel type")

        setting1 = "Channel_" + chan + "_1"
        setting2 = "Channel_" + chan + "_2"
        setting3 = "Channel_" + chan + "_3"

        if chantype == 0:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(130).getLabel2())
        elif chantype == 1:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(142).getLabel())
        elif chantype == 2:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(152).getLabel())
        elif chantype == 3:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(162).getLabel())
        elif chantype == 4:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(172).getLabel())
        elif chantype == 5:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(182).getLabel())
        elif chantype == 6:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(192).getLabel())

            if self.getControl(194).isSelected():
                ADDON_SETTINGS.setSetting(setting2, str(MODE_ORDERAIRDATE))
            else:
                ADDON_SETTINGS.setSetting(setting2, "0")
        
        elif chantype == 7:
            ADDON_SETTINGS.setSetting(setting1, self.getControl(200).getLabel())
            ADDON_SETTINGS.setSetting(setting3, self.getControl(201).getText())
            self.log('self.getControl(201).getLabel() = ' + str(self.getControl(201).getText()))
            
        elif chantype == 9999:
            ADDON_SETTINGS.setSetting(setting1, '')
            ADDON_SETTINGS.setSetting(setting2, '')
            ADDON_SETTINGS.setSetting(setting3, '')

        if self.savedRules:
            self.saveRules(self.channel)

        # Check to see if the user changed anything
        set1 = ''
        set2 = ''
        set3 = ''

        try:
            set1 = ADDON_SETTINGS.getSetting(setting1)
            set2 = ADDON_SETTINGS.getSetting(setting2)
            set3 = ADDON_SETTINGS.getSetting(setting3)
        except:
            pass

        if chantype != self.channel_type or set1 != self.setting1 or set2 != self.setting2 or set3 != self.setting3 or self.savedRules:
            self.madeChanges = 1
            ADDON_SETTINGS.setSetting('Channel_' + chan + '_changed', 'True')

        self.log("saveSettings return")


    def cancelChan(self):
        ADDON_SETTINGS.setSetting("Channel_" + str(self.channel) + "_type", str(self.channel_type))
        ADDON_SETTINGS.setSetting("Channel_" + str(self.channel) + "_1", self.setting1)
        ADDON_SETTINGS.setSetting("Channel_" + str(self.channel) + "_2", self.setting2)
        ADDON_SETTINGS.setSetting("Channel_" + str(self.channel) + "_3", self.setting3)


    def hideChanDetails(self):
        self.getControl(106).setVisible(False)

        for i in range(NUMBER_CHANNEL_TYPES):
            try:
                self.getControl(120 + i).setVisible(False)
            except:
                pass

        self.setFocusId(102)
        self.getControl(105).setVisible(True)
        self.showingList = True
        self.updateListing(self.channel)
        self.listcontrol.selectItem(self.channel - 1)


    def onClick(self, controlId):
        self.log("onClick " + str(controlId))
        if controlId == 102:        # Channel list entry selected
            self.getControl(105).setVisible(False)
            self.getControl(106).setVisible(True)
            self.channel = self.listcontrol.getSelectedPosition() + 1
            self.changeChanType(self.channel, 0)
            if self.checkRules(self.channel) == True:
                self.getControl(114).setLabel('[B]$LOCALIZE[10038] $LOCALIZE[5][/B]*')
            else:
                self.getControl(114).setLabel('[B]$LOCALIZE[10038] $LOCALIZE[5][/B]')
            self.setFocusId(110)
            self.showingList = False
            self.savedRules = False


        elif controlId == 110 or controlId == 111 or controlId == 109:
            ChannelTypeOptions = ("Custom Playlist", "TV Network", "Movie Studio", "TV Genre", "Movie Genre", "Mixed Genre", "TV Show", "Directory", "None")
            ChannelType = xbmcgui.Dialog().select("Choose A Channel Type",ChannelTypeOptions)
            if ChannelType == 8:
                ChannelType = 9999
            if ChannelType != -1:
                self.setChanType(self.channel, ChannelType)
        elif controlId == 112:      # Ok button
            if self.showingList == False:
                self.saveSettings()
                self.hideChanDetails()
            else:
                if self.madeChanges == 1:
                    ADDON_SETTINGS.writeSettings()
                    self.writeToggleSetting()
                    if CHANNEL_SHARING:
                        realloc = ADDON.getSetting('SettingsFolder')
                        FileAccess.copy(SETTINGS_LOC + '/settings2.xml', realloc + '/settings2.xml')
                self.close()
        elif controlId == 113:      # Cancel button
            if self.showingList == False:
                self.cancelChan()
                self.hideChanDetails()
            else:
                self.close()
        elif controlId == 114:      # Rules button
            self.myRules.ruleList = self.ruleList
            self.myRules.doModal()

            if self.myRules.wasSaved == True:
                self.ruleList = self.myRules.ruleList
                self.savedRules = True
        elif controlId == 130:      # Playlist-type channel, playlist button
            dlg = xbmcgui.Dialog()
            retval = dlg.browse(1, "Channel " + str(self.channel) + " Playlist", "files", ".xsp", False, False, "special://videoplaylists/")

            if retval != "special://videoplaylists/":
                self.getControl(130).setLabel(self.getSmartPlaylistName(retval), label2=retval)
        elif controlId == 140 or controlId == 141:      # Network TV channel
            ListOptions = self.networkList
            ListChoice = xbmcgui.Dialog().select("Choose A Network", ListOptions)
            if ListChoice != -1:
                self.setListData(self.networkList, 142, ListChoice)
        elif controlId == 150 or controlId == 151:      # Movie studio channel
            ListOptions = self.studioList
            ListChoice = xbmcgui.Dialog().select("Choose A Studio", ListOptions)
            if ListChoice != -1:
                self.setListData(self.studioList, 152, ListChoice)
        elif controlId == 160 or controlId == 161:      # TV Genre channel
            ListOptions = self.showGenreList
            ListChoice = xbmcgui.Dialog().select("Choose A Genre", ListOptions)
            if ListChoice != -1:
                self.setListData(self.showGenreList, 162, ListChoice)
        elif controlId == 170 or controlId == 171:      # Movie Genre channel
            ListOptions = self.movieGenreList
            ListChoice = xbmcgui.Dialog().select("Choose A Genre", ListOptions)
            if ListChoice != -1:
                self.setListData(self.movieGenreList, 172, ListChoice)
        elif controlId == 180 or controlId == 181:      # Mixed Genre channel
            ListOptions = self.mixedGenreList
            ListChoice = xbmcgui.Dialog().select("Choose A Genre", ListOptions)
            if ListChoice != -1:
                self.setListData(self.mixedGenreList, 182, ListChoice)
        elif controlId == 190 or controlId == 191:      # TV Show channel
            ListOptions = self.showList
            ListChoice = xbmcgui.Dialog().select("Choose A Show", ListOptions)
            if ListChoice != -1:
                self.setListData(self.showList, 192, ListChoice)
        elif controlId == 200:      # Directory channel, select
            dlg = xbmcgui.Dialog()
            retval = dlg.browse(0, "Channel " + str(self.channel) + " Directory", "files")

            if len(retval) > 0:
                self.getControl(200).setLabel(retval)

        self.log("onClick return")

    def writeToggleSetting(self):
        #called on OK to massage the data into what Kodi needs to save in the Settings file
        bad_chars = "[]' "
        
        self.log('TGGL toggles to write: ' + str(self.toggles))
        
        i = 0
        while i < self.toggleLen:
            currentToggle = self.toggles[i][0]
        
            fixedChannelArray = str(self.toggles[i][1])
            
            for c in bad_chars: 
                fixedChannelArray = fixedChannelArray.replace(c, "")
                
            ADDON.setSetting(currentToggle, fixedChannelArray)
            
            i += 1
        
        
         
    def saveToggleSetting(self, currentToggle, fixedChannelArray, i):
        #called by updateToggles to update the master array - does not write back to settings file
        
        fixedChannelArray = list(set(fixedChannelArray))
        fixedChannelArray = sorted(fixedChannelArray)
        
        self.log('TGGL fixedChannelArray: ' + str(fixedChannelArray))
        
        self.toggles[i][1] = fixedChannelArray
        
        self.log('TGGL toggles updated: ' + str(self.toggles))        
    
    def updateToggles(self,origchannel,newchannel,action):
        #called by Copy and Delete channel
        self.log('TGGL updateToggles origchannel: ' + str(origchannel) + ' newchannel: ' + str(newchannel) + ' action: ' + action)
        origchannel = str(origchannel)
        newchannel = str(newchannel)
        
        if action == 'copy':
            self.log ('TGGL Update pre-copy self.toggles: ' + str(self.toggles))
            
            i = 0
            while i < self.toggleLen:
                
                currentToggle = self.toggles[i][0]
                
                self.log('TGGL currentToggle: ' + currentToggle)
                self.log('TGGL currentToggleChannels: ' + str(self.toggles[i][1]))
                
                #first clear the toggle from destination channel (newchannel)
                if newchannel in self.toggles[i][1]:
                    fixedChannelArray = []
                    
                    self.toggles[i][1].remove(newchannel)
                    self.log('TGGL currentToggleChannels pre-copy clear: ' + str(self.toggles[i][1]))
                    
                    self.saveToggleSetting(currentToggle, self.toggles[i][1], i)
                    
                #then update the toggles based on what was copied (origchannel)
                if origchannel in self.toggles[i][1]:
                    fixedChannelArray = []
                    
                    self.toggles[i][1].append(newchannel)
                    self.log('TGGL currentToggleChannels post append: ' + str(self.toggles[i][1]))
                    
                    self.saveToggleSetting(currentToggle, self.toggles[i][1], i)
                    
                i += 1
                    
        elif action == 'clear':
            
            i = 0
            while i < self.toggleLen:
                
                currentToggle = self.toggles[i][0]
                
                self.log('TGGL currentToggle: ' + currentToggle)
                self.log('TGGL currentToggleChannels: ' + str(self.toggles[i][1]))
                
                if origchannel in self.toggles[i][1]:
                    
                    fixedChannelArray = []
                    
                    self.toggles[i][1].remove(origchannel)
                    self.log('TGGL currentToggleChannels post removal: ' + str(self.toggles[i][1]))
                    
                    self.saveToggleSetting(currentToggle, self.toggles[i][1], i)
                
                i += 1
        else:
            self.log('TGGL updateToggles - invalid action: ' + action)
    
    def copyChannel(self,origchannel,newchannel):
        self.log("TGGL copyChannel channel from: " + str(origchannel) + ' to: ' + str(newchannel))
        chantype = 9999
        chan = str(origchannel)
        newchan = str(newchannel)
        set1 = ''
        set2 = ''

        try:
            chantype = int(ADDON_SETTINGS.getSetting("Channel_" + chan + "_type"))
            self.log("TGGL chantype: " + str(chantype))

        except:
            self.log("TGGL Unable to get channel type")

        setting1 = "Channel_" + chan + "_1"
        setting2 = "Channel_" + chan + "_2"
        setting3 = "Channel_" + chan + "_3"
        settingnewtype = "Channel_" + newchan + "_type"
        settingnew1 = "Channel_" + newchan + "_1"
        settingnew2 = "Channel_" + newchan + "_2"
        settingnew3 = "Channel_" + newchan + "_3"

        if chantype == 9999:
            ADDON_SETTINGS.setSetting(setting1, '')
            ADDON_SETTINGS.setSetting(setting2, '')
            ADDON_SETTINGS.setSetting(setting3, '')
        elif chantype == 6:
            oldval = ADDON_SETTINGS.getSetting(setting1)
            oldval2 = ADDON_SETTINGS.getSetting(setting2)
            ADDON_SETTINGS.setSetting(settingnewtype, str(chantype))
            ADDON_SETTINGS.setSetting(settingnew1, oldval)
            ADDON_SETTINGS.setSetting(settingnew2, oldval2)
        elif chantype == 7:
            oldval = ADDON_SETTINGS.getSetting(setting1)
            oldval3 = ADDON_SETTINGS.getSetting(setting3)
            ADDON_SETTINGS.setSetting(settingnewtype, str(chantype))
            ADDON_SETTINGS.setSetting(settingnew1, oldval)
            ADDON_SETTINGS.setSetting(settingnew3, oldval3)
        else:
            oldval = ADDON_SETTINGS.getSetting(setting1)
            ADDON_SETTINGS.setSetting(settingnewtype, str(chantype))
            ADDON_SETTINGS.setSetting(settingnew1, oldval)
        self.loadRules(origchannel)
        self.saveRules(newchan)
        ADDON_SETTINGS.setSetting('Channel_' + newchan + '_changed', 'True')
        self.madeChanges = 1
        self.updateListing(newchannel)
        self.updateToggles(origchannel,newchannel,'copy')
        
        self.log("copyChannel return")

    def clearChannel(self, curchan):
        self.log("clearChannel channel " + str(curchan))
        ADDON_SETTINGS.setSetting("Channel_" + str(curchan) + "_type", "9999")
        ADDON_SETTINGS.setSetting("Channel_" + str(curchan) + "_1", "")
        ADDON_SETTINGS.setSetting("Channel_" + str(curchan) + "_2", "")
        try:
            rulecount = int(ADDON_SETTINGS.getSetting('Channel_' + str(curchan) + "_rulecount"))
            self.log("rulecount: " + str(rulecount))
            for i in range(rulecount):
                ADDON_SETTINGS.setSetting("Channel_" + str(curchan) + "_rule_" + str(i) + "_id", "")
                self.log("Channel_" + str(curchan) + "_rule_" + str(i) + "_id")
            ADDON_SETTINGS.setSetting("Channel_" + str(curchan) + "_rulecount", "0")
        except:
            pass
        self.updateListing(curchan)
        self.madeChanges = 1
        
        self.updateToggles(curchan,0,'clear')
        
        self.log("clearChannel return")

    def swapChannel(self, curchan,swapToChannel,firstEmpty):
        self.log("swapChannel channel " + str(curchan))
        
        self.copyChannel(curchan,firstEmpty)
        self.copyChannel(swapToChannel,curchan)
        self.copyChannel(firstEmpty,swapToChannel)
        self.clearChannel(firstEmpty)
        self.log("swapChannel return")

    def insertChannel(self,curchan,firstEmpty):
        self.log("TGGL insertChannel channel " + str(curchan))
        for i in range(firstEmpty, curchan-1, -1):
            self.copyChannel(i,i+1)
        self.clearChannel(curchan)
        self.log("insertChannel return")

    def deleteChannel(self,curchan,firstEmpty):
        self.log("deleteChannel channel " + str(curchan))
        for i in range(curchan+1, firstEmpty):
            self.copyChannel(i, i-1)
            self.clearChannel(i)
        self.madeChanges = 1
        self.log("deleteChannel return")

    def setListData(self, thelist, controlid, val):
        self.getControl(controlid).setLabel(thelist[val])

    def getSmartPlaylistName(self, fle):
        self.log("getSmartPlaylistName " + fle)
        fle = xbmcvfs.translatePath(fle)

        try:
            xml = FileAccess.open(fle, "r")
        except:
            self.log('Unable to open smart playlist')
            return ''

        try:
            dom = parse(xml)
        except:
            xml.close()
            self.log("getSmartPlaylistName return unable to parse")
            return ''

        xml.close()

        try:
            plname = dom.getElementsByTagName('name')
            self.log("getSmartPlaylistName return " + plname[0].childNodes[0].nodeValue)
            return plname[0].childNodes[0].nodeValue
        except:
            self.log('Unable to find element name')

        self.log("getSmartPlaylistName return")


    def setChanType(self, channel, val):
        self.log("setChanType " + str(channel) + ", " + str(val))
        chantype = 9999

        try:
            chantype = int(ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_type"))
        except:
            self.log("Unable to get channel type")

        chantype = val

        ADDON_SETTINGS.setSetting("Channel_" + str(channel) + "_type", str(chantype))

        for i in range(NUMBER_CHANNEL_TYPES):
            if i == chantype:
                self.getControl(120 + i).setVisible(True)
                self.getControl(110).controlDown(self.getControl(120 + ((i + 1) * 10)))

                try:
                    self.getControl(111).controlDown(self.getControl(120 + ((i + 1) * 10 + 1)))
                except:
                    self.getControl(111).controlDown(self.getControl(120 + ((i + 1) * 10)))
            else:
                try:
                    self.getControl(120 + i).setVisible(False)
                except:
                    pass

        self.fillInDetails(channel)
        self.log("setChanType return")

    def changeChanType(self, channel, val):
        self.log("changeChanType " + str(channel) + ", " + str(val))
        chantype = 9999

        try:
            chantype = int(ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_type"))
        except:
            self.log("Unable to get channel type")

        if val != 0:
            chantype += val

            if chantype < 0:
                chantype = 9999
            elif chantype == 10000:
                chantype = 0
            elif chantype == 9998:
                chantype = NUMBER_CHANNEL_TYPES - 1
            elif chantype == NUMBER_CHANNEL_TYPES:
                chantype = 9999

            ADDON_SETTINGS.setSetting("Channel_" + str(channel) + "_type", str(chantype))
        else:
            self.channel_type = chantype
            self.setting1 = ''
            self.setting2 = ''
            self.setting3 = ''

            try:
                self.setting1 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_1")
                self.setting2 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_2")
                self.setting3 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_3")
            except:
                pass

        for i in range(NUMBER_CHANNEL_TYPES):
            if i == chantype:
                self.getControl(120 + i).setVisible(True)
                self.getControl(110).controlDown(self.getControl(120 + ((i + 1) * 10)))

                try:
                    self.getControl(111).controlDown(self.getControl(120 + ((i + 1) * 10 + 1)))
                except:
                    self.getControl(111).controlDown(self.getControl(120 + ((i + 1) * 10)))
            else:
                try:
                    self.getControl(120 + i).setVisible(False)
                except:
                    pass

        self.fillInDetails(channel)
        self.log("changeChanType return")


    def fillInDetails(self, channel):
        self.log("fillInDetails " + str(channel))
        self.getControl(104).setLabel("Channel " + str(channel))
        chantype = 9999
        chansetting1 = ''
        chansetting2 = ''
        chansetting3 = ''

        try:
            chantype = int(ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_type"))
            chansetting1 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_1")
            chansetting2 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_2")
            chansetting3 = ADDON_SETTINGS.getSetting("Channel_" + str(channel) + "_3")
        except:
            self.log("Unable to get some setting")

        self.getControl(109).setLabel(self.getChanTypeLabel(chantype))

        if chantype == 0:
            plname = self.getSmartPlaylistName(chansetting1)

            if len(plname) == 0:
                chansetting1 = ''

            self.getControl(130).setLabel(self.getSmartPlaylistName(chansetting1), label2=chansetting1)
        elif chantype == 1:
            self.getControl(142).setLabel(self.findItemInList(self.networkList, chansetting1))
        elif chantype == 2:
            self.getControl(152).setLabel(self.findItemInList(self.studioList, chansetting1))
        elif chantype == 3:
            self.getControl(162).setLabel(self.findItemInList(self.showGenreList, chansetting1))
        elif chantype == 4:
            self.getControl(172).setLabel(self.findItemInList(self.movieGenreList, chansetting1))
        elif chantype == 5:
            self.getControl(182).setLabel(self.findItemInList(self.mixedGenreList, chansetting1))
        elif chantype == 6:
            self.getControl(192).setLabel(self.findItemInList(self.showList, chansetting1))
            self.getControl(194).setSelected(chansetting2 == str(MODE_ORDERAIRDATE))
        elif chantype == 7:
            if (chansetting1.find('/') > -1) or (chansetting1.find('\\') > -1):
                plname = self.getSmartPlaylistName(chansetting1)

                if len(plname) != 0:
                    chansetting1 = ''
            else:
                chansetting1 = ''

            self.getControl(200).setLabel(chansetting1)
            self.getControl(201).setText(chansetting3)
        self.loadRules(channel)
        self.log("fillInDetails return")


    def loadRules(self, channel):
        self.log("loadRules")
        self.ruleList = []
        self.myRules.allRules

        try:
            rulecount = int(ADDON_SETTINGS.getSetting('Channel_' + str(channel) + '_rulecount'))

            for i in range(rulecount):
                ruleid = int(ADDON_SETTINGS.getSetting('Channel_' + str(channel) + '_rule_' + str(i + 1) + '_id'))

                for rule in self.myRules.allRules.ruleList:
                    if rule.getId() == ruleid:
                        self.ruleList.append(rule.copy())

                        for x in range(rule.getOptionCount()):
                            self.ruleList[-1].optionValues[x] = ADDON_SETTINGS.getSetting('Channel_' + str(channel) + '_rule_' + str(i + 1) + '_opt_' + str(x + 1))

                        foundrule = True
                        break
        except:
            self.ruleList = []

    def checkRules(self, channel):
        self.log("checkRules")
        rulecheck = False
        try:
            rulecount = int(ADDON_SETTINGS.getSetting('Channel_' + str(channel) + '_rulecount'))
            self.log("Channel " + str(channel) + "rulecount: " + str(rulecount))
            if rulecount > 0:
               rulecheck = True
        except:
            rulecheck = False
        return rulecheck

    def saveRules(self, channel):
        self.log("saveRules")
        rulecount = len(self.ruleList)
        ADDON_SETTINGS.setSetting('Channel_' + str(channel) + '_rulecount', str(rulecount))
        index = 1

        for rule in self.ruleList:
            ADDON_SETTINGS.setSetting('Channel_' + str(channel) + '_rule_' + str(index) + '_id', str(rule.getId()))

            for x in range(rule.getOptionCount()):
                ADDON_SETTINGS.setSetting('Channel_' + str(channel) + '_rule_' + str(index) + '_opt_' + str(x + 1), rule.getOptionValue(x))

            index += 1


    def findItemInList(self, thelist, item):
        loitem = item.lower()

        for i in thelist:
            if loitem == i.lower():
                return item

        if len(thelist) > 0:
            return thelist[0]

        return ''

    def getChanTypeLabel(self, chantype):
        if chantype == 0:
            return LANGUAGE(30181)
        elif chantype == 1:
            return LANGUAGE(30182)
        elif chantype == 2:
            return LANGUAGE(30183)
        elif chantype == 3:
            return LANGUAGE(30184)
        elif chantype == 4:
            return LANGUAGE(30185)
        elif chantype == 5:
            return LANGUAGE(30186)
        elif chantype == 6:
            return LANGUAGE(30187)
        elif chantype == 7:
            return LANGUAGE(30189)
        elif chantype == 9999:
            return LANGUAGE(30164)

        return ''

    def prepareConfig(self):
        self.log("prepareConfig")
        self.showList = []
        self.getControl(105).setVisible(False)
        self.getControl(106).setVisible(False)
        chnlst = ChannelList()
        chnlst.fillTVInfo()
        chnlst.fillMovieInfo()
        self.mixedGenreList = chnlst.makeMixedList(chnlst.showGenreList, chnlst.movieGenreList)
        self.networkList = chnlst.networkList
        self.studioList = chnlst.studioList
        self.showGenreList = chnlst.showGenreList
        self.movieGenreList = chnlst.movieGenreList

        for i in range(len(chnlst.showList)):
            self.showList.append(chnlst.showList[i][0])

        self.showList.sort()

        self.mixedGenreList.sort(key=lambda x: x.lower())
        self.listcontrol = self.getControl(102)

        for i in range(self.maxNeededChannels):
            theitem = xbmcgui.ListItem()
            theitem.setLabel(str(i + 1))
            self.listcontrol.addItem(theitem)

        self.updateListing()
        self.getControl(105).setVisible(True)
        self.getControl(106).setVisible(False)
        self.setFocusId(102)
        self.log("prepareConfig return")

    def findFirstEmpty(self, channel):
        self.log("findFirstEmpty")
        start = channel
        end = self.maxNeededChannels

        for i in range(start, end):
            self.log(str(i))
            try:
                chantype = int(ADDON_SETTINGS.getSetting("Channel_" + str(i) + "_type"))
                if chantype == 9999 and i !=start:
                    return i
                    break
            except:
                self.log("Exception finding first empty")
                return i
                break
        self.log("findFirstEmpty return")


    def updateListing(self, channel = -1):
        self.log("updateListing")
        start = 0
        end = self.maxNeededChannels

        if channel > -1:
            start = channel - 1
            end = channel

        for i in range(start, end):
            theitem = self.listcontrol.getListItem(i)
            chantype = 9999
            chansetting1 = ''
            chansetting2 = ''
            chansetting3 = ''
            newlabel = ''

            try:
                chantype = int(ADDON_SETTINGS.getSetting("Channel_" + str(i + 1) + "_type"))
                chansetting1 = ADDON_SETTINGS.getSetting("Channel_" + str(i + 1) + "_1")
                chansetting2 = ADDON_SETTINGS.getSetting("Channel_" + str(i + 1) + "_2")
                chansetting3 = ADDON_SETTINGS.getSetting("Channel_" + str(i + 1) + "_3")
            except:
                pass

            if chantype == 0:
                newlabel = self.getSmartPlaylistName(chansetting1)
            elif chantype == 1 or chantype == 2 or chantype == 5 or chantype == 6:
                newlabel = chansetting1
            elif chantype == 3:
                newlabel = chansetting1 + " TV"
            elif chantype == 4:
                newlabel = chansetting1 + " Movies"
            elif chantype == 7:
                if chansetting1[-1] == '/' or chansetting1[-1] == '\\':
                    newlabel = os.path.split(chansetting1[:-1])[1]
                else:
                    newlabel = os.path.split(chansetting1)[1]


            #if uncommented (replacing the final line), this would put a marker on the main channel list indicating which channels had advanced rules
            #ruleMarker = ''
            #if self.checkRules(str(i+1)) == True:
            #    ruleMarker = "*"

            #theitem.setLabel2(newlabel + ruleMarker)
            theitem.setLabel2(newlabel)

        self.log("updateListing return")

mydialog = ConfigWindow("script.pseudotv.ChannelConfig.xml", CWD, "default")
del mydialog
