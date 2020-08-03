![PseudoTV logo](https://github.com/fnord12/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

PseudoTV 4.5.2 update - fnord12 branch
======

This release adds a few minor features.  No progress on the Reset Problem (Known Issue #10), unfortunately.

### Alternate Colors for EPG

As requested (as a side issue on issue #14), it's now possible to designate that channels on the episode guide appear in colors.  In Settings under Visuals, you can now input a comma-separated list for three alternate colors.  The idea is that you can designate all your movie channels as one color, all your cartoon channels as another, etc..  By default, the new colors are blue, purple, and green.  But you can modify these yourself by editing the image files under \resources\skins\default\media.  Note that - extending an idea from 4.5.0 - there are also options for short videos in each of the alternate colors, in case you want your commercials (for example) to be different than the regular programming.

### EPG Rowcount

Instead of just the standard 6 channel rows in the episode guide, it's now possible to specify under Settings>Visuals whether you'd like by default to see 3, 6, or 9 rows.  The 3 row grid also hides the info and header, allowing you to see more of the video.  3 is useful if you want to keep watching something while you see what else is on, and 9 obviously allows you to see more of your channel options at once.  In addition to the default setting, you can toggle the number of rows while the guide is up.  The toggle button is mapped to your ACTION_NEXT_PICTURE key, if you have one (it's normally used for Picture Slideshows in Kodi).  If not you can map it to any key by editing your Keymap in the GLOBAL section (NOT the FullscreenVideo section) like so (mapping to the W button in my example, you can pick what you want):

```
<keymap>
    <global>
        <keyboard>
		<!-- leave other stuff already here -->
			
		<w>NextPicture</w>
	</keyboard>
    </global>
	
<!-- leave other stuff already here -->
	
</keymap>
```

Note that this feature required creation of new EGP.xml skin files under \resources\skins\default\1080i.  If you're using a customized skin for PSTV, you'll have to copy my modifications (adding and changing the placement of the channel rows).


### Change Language

This feature gives you the option to have a channel always change to a designated audio language (if available).  I had two use cases for this.  The first is that my wife likes to keep her high school French from getting rusty, so i created a channel with cartoons that happened to have a french audio track.  This feature ensures that the channel will always switch to the French audio track.  Another use case is that for my anime channels, I always want the audio to be in Japanese (and then my separate Autosub add-on will enable the subtitles).   In the first use case, I didn't want Kodi to play the cartoons in French when playing them on another channel or directly in Kodi (by default, Kodi will retain the last video settings, including the language stream).  So it's possible to set a return language, the language to switch back to when leaving the channel.  So if you input "fre, eng" it will change to French when switching to the channel, and switch back to English when leaving the channel.  If you don't need a switch-back, you can just input a single three-letter code.

There are two sets of inputs for this under Settings>Tweaks, so that you can designate channels for uo to two languages.  For the Channels input, you can input a comma-separated list of channel numbers.  For the Change To Change Back field, input a 3 letter language code, or two 3 letter codes separated by a comma if you want to use the Change Back feature.

### Minor fixes

* If for some reason Kodi is unable to create a channel bug/watermark, it will try using any existing watermark files before using the generic PSTV logo (see issue #16).

* For the Don't Include A Show advanced rule, the system will provide a list of your shows to pick from, instead of having to manually type the show name (see issue #12).

* Fixed a very minor issue related to the Channel Logo advanced rule where it was trying to use deprecated Kodi language values for Yes and No that no longer exist.  I've instead hard-coded the choices to "Yes" and "No". Sorry to non-English users but it's still an improvement from the blank values!  I doubt anyone was really affected by this but it's something i ran into when addressing the above Don't Include A Show advanced rule improvement. 

* Fixed a bug in Reset Watch where it was failing to reset videos added during a session.
