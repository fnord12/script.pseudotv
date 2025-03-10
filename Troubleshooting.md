![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

Troubleshooting
======
Please always report your OS, your Kodi version, and confirm that you're on my latest version if you're having a problem.   

WHEN REPORTING A PROBLEM, I NEED A DEBUG LOG PASTED TO https://paste.kodi.tv/

For details, see https://kodi.wiki/view/Log_file

Without that log information we're going to have a lot of back and forth and I won't be able to help, so please follow the instructions at the above link (except paste the link on my github, not the forum).


## Clean install

Before asking for my help, especially if you are having an issue that no one else seems to be having, you may just want to completely remove PSTV and do a clean install.  

First thing to do is to make sure your PSTV settings are backed up.  You can back up your settings by making a copy of \userdata\addon_data\script.pseudotv.  To find your userdata folder, see here:
 
https://kodi.wiki/view/Userdata#Location_of_the_userdata_folder
 
You can copy the entire script.pseudotv folder and put it somewhere safe.
 
After you've done that, uninstall PSTV via the Kodi addons menu. Then close Kodi see if you can verify that the pstv folder has been removed from the Addons folder.  Addons is a peer of Userdata, so should be able to find it by going to the parent folder of Userdata (i'm not sure if this is true in every OS, though).  Look for a folder again called "script.pseudotv".  It shouldn't still be there, but if it is, delete it.
 
Then install my latest version of PSTV.  If everything is now working but you've lost your channel setup, restore your userdata.  MAKE SURE TO PUT IT BACK IN \userdata\addon_data NOT \addons!

## Some Common Issues
If PSTV is not finding videos, confirm that you have FFMPEG installed and/or try setting default video lengths in the Settings>Performance section.

If a custom playlist for TV shows is not playing/populating, make sure it is of Type = Episodes, not Type = TVShow

Generally:
The best thing to do is enable debugging, start PseudoTV, and then stop it, turn off debugging and open the Kodi log.   If you search for the word Exception you should find any current errors and a lot of the time it will tell give you a hint.  You can also search for "failed to find duration".   The debugging for PseuoTV is pretty verbose so you should be able to trace through various problems.   If all else fails post the log as described above so I can see what's going on.
