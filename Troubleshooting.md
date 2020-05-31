![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

Troubleshooting
======
Please always report your OS, your Kodi version, and confirm that you're on my latest version if you're having a problem. Note that i'm really only supporting Kodi 18 right now.

## Crashes and other obvious errors

If you are going to report a bug, especially a crash or freeze, I ask that you provide me with a debug log.  The steps to activate debug mode in Kodi and find your log are here:

https://kodi.wiki/view/Log_file

You don't have to provide me with the full log, just everything in the period where you have activated the debugger through the reproduction of the problem.  You can search for "Log level changed to "LOG_LEVEL_DEBUG_FREEMEM" and give me everything after that.  It will be long - PSTV writes a lot to the log in debug mode, which will help me fix your problem! - so please follow the instructions and put the info on a paste site.  Don't paste it in the Issue area here.

## Clean install

Before asking for my help, especially if you are having an issue that no one else seems to be having, you may just want to completely remove PSTV and do a clean install.  

First thing to do is to make sure your PSTV settings are backed up.  You can back up your settings by making a copy of \userdata\addon_data\script.pseudotv.  To find your userdata folder, see here:
 
https://kodi.wiki/view/Userdata#Location_of_the_userdata_folder
 
You can copy the entire script.pseudotv folder and put it somewhere safe.  (Note also that the Backup program available in the Kodi repository backs these files up if you set it to include Addon Data.)
 
After you've done that, uninstall PSTV via the Kodi addons menu. Then close Kodi see if you can verify that the pstv folder has been removed from the Addons folder.  Addons is a peer of Userdata, so should be able to find it by going to the parent folder of Userdata (i'm not sure if this is true in every OS, though).  Look for a folder again called "script.pseudotv".  It shouldn't still be there, but if it is, delete it.
 
Then install my latest version of PSTV.  If everything is now working but you've lost your channel setup, restore your userdata.  MAKE SURE TO PUT IT BACK IN \userdata\addon_data NOT \addons!