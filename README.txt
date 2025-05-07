Allow to remote control Beamicon2 from Python

https://www.autohotkey.com/docs/v1/KeyList.htm#numpad

USAGE remote_control.py:
  python -m ahkpy .\ahkpy_beamicon\__init__.py

  python remote_control.py # setup to write ahkpy_beamicon.json file.
  You have to move the mouse then press F1 to some locations so that auto clicking works.
  That's required because size may depend on font sizes etc.

USAGE as library;
  See remote_control.py, optionally call setup_external_keyboard()

ROADMAP/TODO:
[prepared]
  This should be moved to Github as its own library
  control beamicon executable using python.ahk
  Felt easier than reverse engineering for prototyping

[partially done]
  Position of elements changes depending no whether menu bar is visible

[ ] fix all important keys using the new BeamiconSettings class
  Here some settings must be updated
  [ ] left/right/top/up/down
  [ ] change speed
  [ ] rewind/stop/start

TODO: REFACTOR:
  [ ] XR XRC etc -> give them nice names so that the code is understandable
      and add configs to configurable_positions
  [ ] think about formulars to make them clickable cause they are two way from
      click to config and from config to click
  [ ] have a config file so that settings can be switched and stored on disk
      rather than in this file
