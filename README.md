![alt text](https://github.com/Steveb1968/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

PseudoTV for Kodi
======

[View branch download information.](#branches-guide)


![screenshot](https://github.com/Steveb1968/script.pseudotv/blob/master/resources/screenshots/screenshot-01.png?raw=true)

### What is it?
It's channel-surfing for your media center. Never again will you have to actually pick what you want to watch. Use an electronic program guide (EPG) to view what's on or select a show to watch. This script will let you create your own channels and, you know, watch them. Doesn't actually sound useful when I have to write it in a readme. Eh, try it and decide if it works for you.

---
### Requirements
This **ONLY** uses your existing video library to play video. It will **NOT** play video from the internet. If you do not have a significant number of videos in your library, then this script probably isn't for you. Sorry.

---
### Features

* Automatic channel creation based on your library.
* Optionally customize the channels you want with the channel configuration tool.
* Utilize the Kodi smart playlist editor to create advanced channel setups.
* Use an EPG and view what was on, is on, and will be on. Would you rather see something that will be on later? Select it and watch it now!
* Want to pause a channel while you watch another? And then come back to it and have it be paused still? Sounds like a weird request to me, but if you want to do it you certainly can. It's a feature!
* An idle-timer makes sure you aren't spinning a hard-drive needlessly all night.

---
### Setup
1. First, install it.  This is self-explanatory (hopefully).  Really, that's all that is necessary.  Default channels will be created without any intervention.  You can choose to setup channels (next step) if you wish.
2. _Instructions to create your own channels:_ Inside of the addon config, you may open the channel configuration tool. Inside of here you can select a channel to modify. You may then select it's type and any options. For a basic setup, that's all you need to do. It's worth noting that you may create a playlist using the smart playlist editor and then select that playlist in the channel config tool (Custom Playlist channel type). Additionally, you may select to add advanced rules to certain channels. There are quite a few rules that are currently available, and hopefully they should be relatively self-explanitory.

	This is a readme and should include descriptions of them all... who knows, maybe it will some day.

---
### Controls
There are only a few things you need to know in order to control everything. First of all, the Stop button ('X') stops the video and exits the script. You may also press the Previous Menu ('Escape\Back') button to do this (don't worry, it will prompt you to verify first). Scroll through channels using the arrow up and down keys, or alternatively by pressing Page up or down. To open the EPG, press the Select key ('Enter'). Move around using the arrow keys. Start a program by pressing Select. Pressing Previous Menu ('Escape\Back') will close the EPG. Press the info key ('I') to display or hide the info window.  When it is displayed, you can look at the previous and next shows on this channel using the arrow keys left and right. To access the video osd window press the context menu key ('C\Menu'), to exit the osd press ('Escape\Back').

---
### Settings

**General Settings -**

* **Configure Channels:** This is the channel configuration tool.  From here you can modify the settings for each individual channel.    
* **Force Channel Reset:** If you want your channels to be reanalyzed then you can turn this on.
* **Time Between Channel Resets:** This is how often your channels will be reset. Generally, this is done automatically based on the duration of the individual channels and how long they've been watched. You can change this to reset every certain time period (day, week, month).
* **Default channel times at startup:** This affects where the channels start playing when the script starts.  Resume will pick everything up where it left off (see release notes regarding a bug here). Random will start each channel in a random spot. Real-Time will act like the script was never shut down, and will play things at the time the EPG said they would play.
* **Background Updating:** The script uses multiple threads to keep channels up to date while other channels are playing. In general, this is fine. If your computer is too slow, though, it may cause stuttering in the video playback. This setting allows you to minimize or disable the use of these background threads.
* **Auto-off Timer:** The amount of time (in minutes) of idle time before the script is automatically stopped.
* **Enable Channel Sharing:** Share the same configuration and channel list between multiple computers. If you're using real-time mode (the default) then you can stop watching one show on one computer and pick it up on the other. Or you can have both computers playing the same lists at the same time.
* **Shared Channels Folder:** If channel sharing is enabled, this is the location available from both computers that will keep the settings and channel information.
* **Reset Watched Status:** If you don't want your viewing in PSTV to affect your playcounts, Continue Watching lists, etc., enable this.  It will take a little time at the end of the session to restore all your counts to how they were before you started.

**Visual Settings -**

* **Info when Changing Channels:** Shows the current media information when changing channels. The duration of the info can be set in the sub-setting "Changing channel info duration".
* **Show channel logo in epg grid:** Will display a logo matching your channel name, if available.
* **Channel Logo Folder:** The place where channel logos are stored.  
* **Always show channel watermark:** Always display the current channel logo watermark. The position of the logo can be adjusted via the sub-setting "Set watermark position" (upper left, upper right, lower right, lower left).
* **Color Watermark:** By default, watermarks are in black & white; this option will display them in color.
* **Watermark Brightness:** After converting the logo to a watermark, adjust the brightness.  Higher than 1 is brighter, lower is darker.
* **Clock Display:** Select between a 12-hour or 24-hour clock in the EPG.

**Tweaks -**

* **Playlist Media Limit:** Limit the playlist items in a channel generated by pseudotv. Smaller values will result in quicker load/rebuild times.  Note: custom playlists are not affected by this; you can instead adjust them in Kodi's playlist editor.
* **OSD Channel Number Color:** Change the color of the channel number located at the top left, seen when changing channels and on startup.
* **Hide leading zeroes for Channels:** If you want to see 5 instead of 05 as your channel label.
* **Seek step forward:** Option to adjust the seek step forward (right arrow key in fullscreen video). Options include 10 sec,30 sec,60 sec,3 min,5 min,10 min,30 min.
* **Seek step backward:** Option to adjust the seek step backward (left arrow key in fullscreen video). Options include -10 sec,-30 sec,-60 sec,-3 min,-5 min,-10 min,-30 min.
* **Start Channel:** Which channel PseudoTV will begin on.
* **Always Use Start Channel:** If not enabled, PseudoTV will remember your last played channel, except when doing a full Channel Reset.

**Information -**
* **Hide year and episode information:** Removes the year (movies) and SxEP (episodes). A force channel reset is needed for the setting to take effect.  
* **Show Coming Up Next box:** A little box will notify you of what's coming up next when the current show is nearly finished.
* **Hide very short videos:** Don't show clips shorter than the "Duration of Short videos" setting. Effects the EPG, coming up next box and the info box. This is helpful if you use bumpers or commercials.  You can configure this to not show the Coming Next box FOR short videos, DURING short videos, and/or on the EPG.
* **Use Episode Title instead of Show Title:**  For channels where the shows are mostly the same, you can show the episode titles instead.  Enter a comma separated list of channel numbers.  You can choose to hide the Show Title entirely or keep it for the Info box.  For Directory channels, there is also an option to hide the title entirely (useful for commercials/bumpers).
* **Don't display individual blocks for these channels:** If you have a channel comprised entirely of short videos or just don't want to display individual shows (e.g. a music video channel) you can use this option to simply show a solid bar that displays the channel name.  Again, input a comma-separated list of channel numbers.
* **Hide Labels on EPG blocks:** For very short videos, the labels will truncate and/or get replaced by elipses.  If you want to hide those and simply display a blank box, input a value indicating the width in pixels that should be affected.  Good values to try are 85,45, or 30, but see what works for you.  You can also potentially change the color of these boxes; see Tips & Tricks #7.

**Performance -** 

* **Max Needed Channels:** The highest number of allowed channels in PSTV is 999.  To avoid cycling through all 999 potential channels, you can tell it how many channels you're actually using to help speed things up a bit.  Please be sure to leave at least one blank channel; it's necessary for some of the Channel Config functionality like Swap and Copy/Paste.  The performance gains here will be minor and to the extent that they'll be seen, it's about not having to go through 999 channels when you only need 200, not about the difference between 150 and 200.  So err on the side of giving yourself some breathing room.
* **Delay Before and After Changing Channel:**  Before determines how many miliseconds before actually changing channels PSTV will take to process things.  After determines how long PSTV blocks you from doing anything (by ignoring your button presses) after changing a channel.  Lowering these values will speed up your channel surfing, but if you see weird effects (too much of the "Working" pop-up, crashes, channels mysteriously resetting), set them back to their defaults.
* **Minimum EPG block size:** By default, PSTV will increase the EPG block size for very short videos to a miminum value.  If you are displaying very short videos, you may find that the EPG occassionally doesn't recognize them when you select them.  Lowering this number (or setting to 0) will eliminate that problem.  But be aware that having to render many boxes can cause lag on the EPG.  So the tradeoff is between accuracy and performance.  If you have alot of short videos and are already experiencing lag on the EPG, you may consider even increasing this value.  (Other options include using the "Hide Short Videos - EPG" or "Don't display individual blocks for this channel" settings.)
* **Skipped Videos:** PSTV engages in a rigorous parsing of your video files and may reject things that even Kodi can play.  The options here can a) alert you to that fact and b) assign a fake duration value to items that PSTV can't read.  The duration could cause problems in the Episode Guide if the default value doesn't match reality (and/or if the video really is corrupted), but it may allow otherwise rejected videos to show up.  In the longrun, you'll want to fix your videos by running them through something like MKVToolNix or FFmpeg, but this will get you going in the meantime.

**Auto Start -**

* **Activate Service:** Activate auto start. Pseudotv will automatically start when kodi is started.
* **Service Delay:** Delay the auto start of Pseudotv at Kodi start-up. This is useful for low end hardware or if your skin loads multi-pal scripts at start-up.
* **Show Notification:** Self explanatory I hope. Will show a notification of Pseudotv's attempt to auto-start.

---
### Tips & Tricks

1. If you are annoyed by the apparance of the seeker bar every time you change a channel, or if you find that sometimes instead of the PSTV Info screen you get the Kodi default/skin Info screen, or if you don't want to see the Seek numbers appear when you input numbers to change a channel, PSTV unfortunately has no control over these things.  But it's easy for you to put in a conditional visiblity for your skin.  The bottom of the readme has the instructions.  The only trick is if you are using the default Estuary skin, you first have to make a copy of it, rename it (inside the addon.xml file too!), and put it in your userdata folder or (better) import it via Addons as a new skin.

**&lsaquo;visible&rsaquo;String.IsEmpty(Window(home).Property(PseudoTVRunning))&lsaquo;/visible&rsaquo;**  
Useful for hiding skin xml files such as DialogBusy.xml/DialogSeekBar.xml and VideoFullScreen.xml
 
**Example: DialogSeekBar.xml**  
Replace *"Player.DisplayAfterSeek"* with  
*"[Player.DisplayAfterSeek\+String.IsEmpty(Window(home).Property(PseudoTVRunning))]"* 

For VideoFullScreen, put the tag at the very top, under the Window tag and/or in the final "Seek Number label" (below the label tags).

2. If you want to create your own logos, they should be in PNG format.  Dimensions of 260x150 work well.

3. If you've adjusted the Watermark options in the Settings (color or brightness), you need to delete the old Watermarks from the ChannelBug folder under \Kodi\userdata\addon_data\script.pseudotv\cache\ChannelBug before new ones will generate.

4. The transparancy of the watermark is a factor of the skin.  If you want to adjust it, under resources\skins, pick a skin and edit TVOverlay. The final setting is "animation effect="fade" end="20" condition="True""; you can adjust the "end" value or simply set the condition to False.^

5. [gils_001 has a great write up of how to use Directory channels and interleaving to create Commercials or Bumpers.](https://www.reddit.com/r/PseudoTV/comments/g5mnbn/issues_and_solutions_with_directory_channels/)

6. This program is meant to run with local files only, but if you are using SMB, try mapping your shares to drives.  If you're using [Libreelec here is how to do it](https://libreelec.wiki/how_to/mount_network_share) and in Windows right click your shares and select map drive and assign a drive letter.  (Thanks to Technobob for this tip.)

7. If you want to adjust the color of your short/de-labeled EPG buttons, you can find pstvButtonNoFocusShort.png and pstvButtonFocusShort.png under resources/skins and edit them how you like.^  I found leaving them the same as the regular buttons worked best for me, but you can experiment with different colors and/or deleting the side borders. 

Finally: If reporting a problem, first see the [Troubleshooting doc](https://github.com/fnord12/script.pseudotv/blob/master/Troubleshooting.md).

^As with anything you customize, just be sure to make a backup before taking a new release.

---
### Branches guide

This version is tested in Kodi 18 Leia only.  It will not work in 19 at this time and updating for that is not high on my priority list.
For older versions, see https://github.com/Steveb1968/script.pseudotv

---
### Credits

**Developer:** Jason102, Steveb, fnord12.<br>
**Code Additions:** Sranshaft, TheOddLinguist, Canuma, rafaelvieiras.<br>
**Skins:** Sranshaft, Zepfan, Steveb.<br>
**Preset Images:** Jtucker1972.<br>
**Languages:** CyberXaz, Machine-Sanctum, rafaelvieiras, Eng2Heb.