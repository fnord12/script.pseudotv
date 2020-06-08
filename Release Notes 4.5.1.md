![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/images/Default.png?raw=true "PseudoTV Logo")

PseudoTV 2.5.1 update - fnord12 branch
======

The headline for this release is: Partial Fix for Resume Problem and EPG Configurability.  Details below.

### Partial Fix for Reset Problem

By splitting the channel-changing function into one for first time channel and one for changing a channel, i seem to have resolved the Reset Problem, with some caveats.

Background: The "Reset Problem" is where the starting channel resets upon reopening PseudoTV during the same session (i.e. prior to the next Channel Update/Force Update) causes the current episode, and sometimes the entire channel, to reset.  This was especially annoying to people who watch in Resume mode (and/or when a channel is set to auto-pause), but it was a problem in Realtime too.  The problem didn't begin with a change in PSTV code; it started happening for Resume/Pause in Kodi 17 and began affecting Realtime in Kodi 18.

In experimenting, i found that reording the function calls within the channel-changing function resolved the problem, seemingly.   I've also removed some of the processing that is done when changing a channel (since it doesn't apply for the first channel) and added a slight delay before Kodi starts.  But really it seems only the reordering has made a difference (The function that makes the channel number label appear is now called before the actual channel change call, instead of after.  There's no noticeable effect for the channel label but the channel no longer resets upon startup.  The fact that a mere order of operation change could "fix" the problem is weird to me, and unfortunately didn't lead to any further insights that helped me fix it further.)

The main caveat is that the fix only works for Realtime mode by default.  If your mode is set to Realtime, when you re-start PSTV your remembered startup channel (assuming you're not using the Start Channel option introduced last release) should now play as if PSTV continued to be on the whole time.  You may briefly see the start of the video before it seeks to the correct time.

It is possible to configure the "fix" to work for Resume mode, but it requires adjusting the code.  You have to open Overlay.py, find def setFirstChannel, and edit the line that assigns the seektime variable (currenly line 452).  You want to remove everything after showTimeOffset so that the new line will be:

```
seektime = self.channels[self.currentChannel - 1].showTimeOffset
```

If you've never worked with Python before, be careful to retain the current spacing/indentations

You would think that this could be handled in the code with a simple if statement, and you will see that commented out in the code.  But for some reason that caused the reset problem.  But hardcoding it for either mode works.

The other caveat is, considering how tempermental this is, it may not actually work for you.  Your hardware and the type of video (and how well encoded it is)  may make a difference.  But it works for me now, and i'm hoping it works for others.  If not, the workaround continues to be to set your Start Channel to a channel where you don't care if it resets.

### EPG Configurability

1. In the last release i introduced the ability to cause an Episode Title to appear in the EPG instead of the Showtitle for Single Show Channels.  The idea was that if you have the same show playing all the time on a channel, you don't need to see the channel show repeated, and the Episode Title is more relevent.  After playing with that, i found i wanted more flexibility:

* I have some channels where it's just a few related shows (e.g. a channel just for Mystery Science Theater and Rifftrax, or a channel with just the old and new Doctor Whos), and i wanted the same option there.  
* On the other hand, i had a few single show channels where i DIDN'T want to lose the Show Title (because i am interleaving that channel into another channel).  

So instead of a single checkbox, there are now two input fields.  You can input a list of channels where you want to swap the Titles and hide the Show Title in the Info box (when you press I), or swap them but still show the Show Title in Info.

You can input a comma separated list in the fields.  The above will only work for Episodes (only they have Episode Titles).

2. There is also a third input field for Directory channels, where you can hide the Title completely.  This is for Commercials and the like, where you don't need the name of the ad showing in the EPG.  (More on that below.)

3. Also in the last release, i tried to introduce some flexibility around the plot descriptions for Directory channels.  Instead of just displaying the file path, it was possible to tweak the description using the language file.  This release replaces that idea with an input field under the channel settings for Directory channels.  You can now input a default plot for a Directory channel (e.g., "Another exciting documentary!).  But it goes a little further than that:

* The following characters will serve as a replacement field that will swap in the name of the file (sans the extension): ==e== 

* You can use the | symbol to input multiple plot descriptions that will be chosen randomly.  

So for example if you have a Directory channel of old game show videos, you could put something like this in the field:

Join BUZZR for ==e==. | Welcome to the time capsule! | Another blast from the past! | BUZZR presents a special showing of ==e==.

And those four plot summaries will now randomly populate your EPG for that channel.  It'll look like a real channel instead of displaying the ugly file path.  The file path will show if you put nothing in the field, for those that prefer that.  And if you want the plot to be totally blank, just input a space.

4. There is also now an option to not display the title in the tiny block (no point in seeing just those ugly elipses).  The number you input should be in pixels, not length.  I've found that 85 hides the labels for most of my music videos.  30 or 45 is a good number if you're just trying to hide commercials.

5. In your skins folder, you will find two new images that represent the new short blocks.  Right now they are the same as the regular sized blocks.  But this gives you the option to change their color so that when you look at the EPG you can see your bumpers/commercials as distinct items from the shows.  I prefer to leave the blocks the same color; they will often just blend into the surrounding episodes, but they can still be selected as distinct things and don't screw up the Info box (as in issue #3). But now the coloring option is available (as with anything you customize, just be sure to make a backup before taking a new release).

6. Alternatively, you can simply cause an entire channel to not show individual boxes - as requested in issue #9.  Again, you can input a comma separated list of channel numbers.

7. I've separated the setting for Hide Short Videos - Coming Up from Hide Short Videos - EPG.

8. I've also addressed an issue where if you WEREN'T hiding short videos, the EPG would sometimes not acknowledge them.  This has to do with the fact that PSTV was automatically resizing small blocks - under 30 pixels - to 30.  This would cause the EPG info to get out of sync.  I've now paramatized this value, under Performance.  I've kept the default at 30 but i've set it to 0 for myself.  But be aware that having to render many boxes can cause lag on the EPG.  So the tradeoff is between accuracy and performance.  If you have alot of short videos and are already experiencing lag on the EPG, you may consider even increasing this value (or possibily hiding short videos or utilizing the "Don't display individual blocks" option (#6 above)).

I've also tweaked my solution to issue #2 and it seems somewhat better now, but it can still sometimes get out of sync if you are hiding short videos from the EPG.  So, as an alternative, you allow your "short videos"/commercials to display in the EPG and utilize some of these new options.  Putting together all of the above updates, here's what you can do:

![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/screenshots/EPG1.png?raw=true "Episode Guide 1")

![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/screenshots/EPG2.png?raw=true "Episode Guide 2")

In the above screenshots, there are short videos interleaved between every show on channel 1.  Note that they are mostly invisible, and even when not they're unobtrusive (the difference between invisible and unobtrusive has to do with the length of the video and other mysterious factors that i can't control).  Note that even when passing over the commercial, it just shows a fun custom plot/message and nothing ugly.

And if you press I during a commercial, it again shows nothing ugly.  (In Hide mode, pressing I during a short video does nothing, which always felt like something was broken to me.) (Also note i've replaced the generic missing video picture with the PSTV logo.)

![alt text](https://github.com/fnord12/script.pseudotv/blob/master/resources/screenshots/Commercial.png?raw=true "Commercial")

Having these options also helps for people who have legitimate short videos that they want to display which overlap in length with commercials.

### Minor bug fixes

* Fixed 2 bugs around the Assigned Duration option added last release.
* Found and addressed an older issue where movies might have been getting skipped (without notification) due to special characters in plot or plotoutline.
* Investigated an older problem where the Interleave Starting Episode kept seemingly getting changed.  Found that there was code that deliberately updated that field upon quitting PSTV.  I don't know why, and commenting out that line seems to have no ill effect (and the number stops getting updated in Config).  Please let me know if you start seeing problems with interleave, but i don't think that will be the case.

Also reorganized the Settings section again.  Most of the new settings are under Information; some of the older settings relating to display of infomration have been moved there as well.

This will most likey be my last release for a while aside from fixing any newly introduced bugs.  Kodi 19 and Python 3 compatibility is on the horizon, but i'm not in a hurry for that.
