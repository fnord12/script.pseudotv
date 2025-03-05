![PseudoTV logo](https://github.com/fnord12/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

PseudoTV 5.0.0 update - fnord12 branch
======

This release brings PseudoTV to Python 3 and updates it to work with Kodi v21 Omega.  It mostly functions the same as always with an important note regarding file lengths.   It is strongly recommended that you instal ffmpeg if using this addon.   See below for details.

Users on version 4.x/Kodi 18 should be able to back-up their current PseudoTV user data (see the Troubleshooting doc) and then restore it to the 5.x/Kodi 21 folder to retain their current channels.

### File Lengths

The problem: A lot of videos floating around have improper headers or other slight problems.  The videoes are usually playable but Kodi does not get their length on the first pass (when the video is first imported).   Kodi usually correctly gets their lengths on a second pass (when the video is first visible in a skin), but that duration data is not stored in a place where PseudoTV can get them from a JSON query.  YOU PROBABLY HAVE MORE VIDEOS IN YOUR LIBRARY LIKE THIS THAN YOU REALIZE.  PseudoTV needs the correct video length in order to properly schedule the shows and display them on the EPG.  Additionally there are Directory channels which contain videos that Kodi doesn't have in the database.

PseudoTV used to try to manually check the video lengths but it could only do so for certain file formats / codecs and increasingly it wasn't working anymore.  Plus it was slow to have to recheck those lengths every time.

So with this version I have dropped to old way to check for file lengths and am instead using FFMPEG.  This requires you to have FFMPEG properly installed on your OS.  FFMPEG is free, open source, widely used, and multi-platform.  For Linux it should be there by default.  For Windows you will have to download it and set the proper path.   Here are instructions for Windows 10 & 11: https://windowsloop.com/install-ffmpeg-windows-10/

I've found you have to reboot your computer after following the above instructions.

After finding a duration for a video using this method, PseudoTV will now write the duration to file, which will mean that next time it shouldn't have to use FFMPEG for that video and it will be able to load faster.   So the first time or maybe first few times you run PseudoTV it may take a little longer to start but it should be much faster after most of your videos have already been checked.

If you choose to not install FFMPEG it you should still be able to run PseudoTV but any videos without proper durations in Kodi will be skipped.   You still have the option to default such videos to a specified length - see the Settings>Performance tab.  The downside of this is that your EPG and the upcoming schedule may not be accurate if the default length is very different than the atualy video lengths (it's not catastrophic; it just means that the wrong show may load when clicking on the EPG).

### Other minor updates

- Reset Watched (prevents PseudoTV from updating your videos' Playcount and Resume data) is now on by default.   It can be turned off in the General settings area.  It is now possible to exclude channels from getting reset for those of you who want PseudoTV to keep track of your watched progress for some channels but not others.

- Now when copying, swapping, inserting, or deleting channels in Channel Configuration, all of the comma-separated channel lists in the main settings area will get updated.  This relates to all of the settings in the main settings area where you input a list of comma separated channels: Exclude from reset, alternate color blocks, the change languages settings, the hide titles options, don't display individual blocks.

### Limitations

- See above regarding file lengths.   If you don't install FFMPEG you may find quite a few videos are not loaded (or are using the default values if set).

- It is no longer possible to use the mouse to select a show from the EPG.  You have to use the arrows and Enter key.  This is due to a change in Kodi that I haven't figured out; I'll have to ask on the forum if this matters to people.

- The problems with using Resume mode as noted in earlier Release Notes remain.  In particular, the starting channel will often reset to the beginning of the show/movie.  Workaround is to set your start channel to something where resetting won't matter.


### Help

- See the other release notes docs for updates since SteveB's branch.
- See the Readme file for explanations of each field in settings and other Tips and Tricks.
- See the Troubleshooting doc which shows how to ask for help and goes through some common problems.
