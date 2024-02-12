## I want to scrub through a track faster

Hold one of the **Search** buttons (either forward or backward will work), and then turn the jog wheel. The needle will scrub at high speed in the direction the jog wheel is turned.

## I want to jump to a hot cue without it playing

Press the hot cue button while touching the surface of the jog wheel. The track will jump to the hot cue location, but will not play until you let go of the jog wheel.

## I want to set the main cue point to a particular hot cue

Using the method above, jump to the hot cue while touching the jog wheel surface. Then, before letting go of the jog wheel, hit the main cue button to set the cue location. When you let go of the jog wheel, the track will remain cued and will not play. This then makes it easy to, for example, set an instant loop from the cued location.

## I want to quickly reset the main cue point to the beginning of the track

Press the backwards **Track Search** button. If not already at the beginning of the track, this button will reset the main cue to the first cue point of the track, and will pause playback. If pressed when already cued at the beginning of the track, the button will skip back to the previous track in the current playlist.

## I want to record the output of the mixer via USB

This will need Rekordbox for first-time audio routing configuration, but once set up, the mixer can simply be used with Audacity or any other DAW as an input source.

Firstly, download the relevant driver from the Pioneer website. For the DJM-450, the page is here: https://www.pioneerdj.com/en/support/software/djm-450/ If installing this on Windows, restart your machine after the install is complete.

To set up the audio routing properly, connect the mixer to the computer and start Rekordbox. Switch to **Performance** mode and then choose **File** -> **Preferences**.

Under the **Audio** tab, ensure the mixer is in **External** mode, and press the **Settings Utility** button in the left column of the table. In this utility, go to the **Mixer Output** tab and make sure that all the dropdown boxes underneath **Mixer Audio Output** are set to **REC OUT**. Under **USB Output Level**, choose the desired headroom (I chose **-10dB**),

Finally, you may have to restart your computer again, or try shutting down the Rekordbox process in the system tray, as this will conflict with Audacity when attempting to record audio from the mixer.
