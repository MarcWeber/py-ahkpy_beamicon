Allow to remote control Beamicon2 from Python

https://www.autohotkey.com/docs/v1/KeyList.htm#numpad

USAGE remote_control.py:
==========================
  python -m ahkpy .\ahkpy_beamicon\__init__.py

  python remote_control.py # setup to write ahkpy_beamicon.json file.
  You have to move the mouse then press F1 to some locations so that auto clicking works.
  That's required because size may depend on font sizes etc.

SETTINGS -> how to configure button positions
=============================================
  Remove the ahkpy_beamicon.json file.

  Then restart.
  Follow the instructions in terminal which ask you to
  move your mouse to locations on the window and press F1 to record the locations.
  1) bottom of window title
  2) bottom of window title + menu bar (text)
  3) bottom of window + toolbar (the icons)
  -> now you have self.getsiizes.T (top of inner window)

  contiue with left side of tab bar on the right and the tob 2 buttons.
  and the top line of the addvertising area

  -> now you have edfined the inner window area which is required to calculate
  positions of play/ stop rewind etc. 

  It should now switch to first tab.
  Follow the guide ..

  It should then switch to second tab
  Follow the guide

  you should be done.

  Now you can press all the numpad key to move start/stop/play and change the moving speed


USAGE as library;
  See remote_control.py, optionally call setup_external_keyboard()

KONWN ISSUES

continuous mode -> key up is not recognized if you hit arrow keys shortly only :-(

ROADMAP/TODO:

  [prepared]
    This should be moved to Github as its own library
    control beamicon executable using python.ahk
    Felt easier than reverse engineering for prototyping

  [partially done]
    Position of elements changes depending no whether menu bar is visible
    Missing: Detect whether menu or toolbar is active (assuming True for now)

  [x] fix all important keys using the new BeamiconSettings class

  [ ] detect active tab (by pixel or so) so that 0.2 seconds waiting can be saved! R3562056818

  [ ] rewrite all code to use action_on_setting because its more simpler
      and all the logic to calculate the positions can be found in 2 functions only
      And it allows to guide the user even more by moving the mouse to the position

  [ ] when setting setting place mouse to last known position unless it's 0 or None

  [ ] review and fix all methods used by the other code
