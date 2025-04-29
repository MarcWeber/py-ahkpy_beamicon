import sys
from dataclasses_json import dataclass_json
import numpy as np
from pathlib import Path
from typing import Callable, Any, TypeVar, Generic, Optional, TypeAlias, cast, Literal, Tuple
# there are more python ahk implementations such as ahk ..
import ahkpy as ahk
import pyperclip as cp
import time
from dataclasses import dataclass

from u_ahkpy import WithWindow

SHADOW_LR = [5, 5]

WindowSize: TypeAlias = np.ndarray
ClickPos: TypeAlias   = np.ndarray

# #NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
# ; #Warn  ; Enable warnings to assist with detecting common errors.
# SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
# SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.
# same for x shadow like 5px

minus_x_zero_buttons = 370
zero_x = 34
zero_d = 40

YP = 20 # TODO
pos_ys = [ YP + 60 , YP + (60.0+150)/2,   YP + 150] # TODO

speed_y_dist = 86 // 4
speeds = {
    "continuous": 301 + 0 * speed_y_dist,
    "10 mm" :     301 + 1 * speed_y_dist,
    "1 mm" :      301 + 2 * speed_y_dist,
    "0.1 mm" :    301 + 3 * speed_y_dist,
    "0.01 mm" :   301 + 4 * speed_y_dist,
}
print(speeds)

def click_rel_window(x: float, y: float):
    ahk.mouse_move(x=x, y=y+T, relative_to="window")
    print("moving %s " % str((x,y)))
    ahk.click()

# each of these settinsg can be set by mouse
# see set_*
BeamiconSettings_configurable = {
        "window_title_height": "move your mouse at the bottom of the window title bar to estimate its height",
        "window_title_height_plus_menu": "move your mouse at the bottom of the menu / navigation bar within beamicon to estimate its heighth",
        "advertising_area_top": "",

        "tab_width": "lefth side of the tab bar on the rigth end of the window",
        "tab_Programm_y": "center of the tab Programm",
        "tab_Einrichten_y": "center of the tab Einrichten",

        "speed_pos_continuous_xy": "", # of drop down's first
        "speed_pos_0_01_xy": "",       # of drop down's last
}

CONFIG_FILE = Path('ahkpy_beamicon.json')

settings_defaults = {
}


beamicon_settings = cast('BeamiconSettings', None) # farward decl

current_window = None
def with_beamicon_main_window(func):
    def wrapper(*args, **kwargs):
        global current_window, beamicon_settings
        before = current_window
        with WithWindow(beamicon_settings.match_beamicon_main) as bw:
            current_window = bw
            try:
                return func(*args, **kwargs)
            finally:
                current_window = before
    return wrapper

@dataclass
class Sizes:
    X: int
    Y: int
    L: int
    W: int
    H: int
    XRY: int
    XRTY: int
    win_inner_width: int
    win_inner_height: int # without navigation/menu bar !, See T
    T: int
    YCWA: int
    Y_cnc_b: int
    XC: int
    c: int
    my: int



# the following configurations are used to find the windows and positions to click on
# and can be stored. Some numbers are derived
@dataclass_json
@dataclass
class BeamiconSettings:

    match_beamicon_main = {"title" : "(.*Beamicon2-Hauptbildschirm.*)|(.*Beamicon2 Mainscreen.*)", "match": "regex"}
    match_beamicon_MDI  = {"title" : "Beamicon2-Basic MDI", "match": "exact"}

    window_title_height: int = 25
    window_title_height_plus_menu: int = 40
    advertising_area_top: int = 80

    tab_width: int =30
    tab_Programm_y: int = 40
    tab_Einrichten_y: int = 40

    speed_pos_continuous_xy: Tuple[int, int] = (0,0) # y counting from #inner_window
    speed_pos_0_01_xy:       Tuple[int, int] = (0,0) # y counting from #inner_window


    @staticmethod
    def from_config_file() -> 'BeamiconSettings':
        if not CONFIG_FILE.exists():
            bs = BeamiconSettings.from_dict(settings_defaults)
            print("BeamiconSettings not setup yet, starting setup(). Please follow instructions")
            bs.setup() # TODO should be async or such
            return bs
        else:
            with CONFIG_FILE.open('r') as f:
                return BeamiconSettings.from_json(f.read())
    @property
    def window(self):
       return WithWindow.current()


    # GLOBAL STATE
    @property
    def TOOLBAR_ACTIVE(self):
        return True # Should find out automatically whether toolbar/menubar is shown - maybe by color ?

    @property
    @with_beamicon_main_window
    def sizes(self) -> Sizes:
        # T = 60 if self.TOOLBAR_ACTIVE else 24
        T = self.window_title_height if self.TOOLBAR_ACTIVE else self.window_title_height_plus_menu
        bw = WithWindow.current()

        X, Y, W, H = bw.x, bw.y, cast(int, bw.width), bw.height
        if (bw.is_maximized):
            R, L = 0, 0
        else:
            R, L = SHADOW_LR

        XRY  =  W - R - 25
        XRTY = W - R

        # without tabs, without menu, without title

        # #inner_window: inner area without tabs, without menu, see T above
        win_inner_width  = XRY - L
        win_inner_height = H   - T

        # Y minus ads -> centered
        YCWA = (win_inner_height - 180) // 2

        return Sizes(X = X,
                Y = Y,
                L = L,
                W = W,
                H = H,
                XRY = XRY,
                XRTY = XRTY,
                win_inner_width = win_inner_width,
                win_inner_height = win_inner_height,
                T = T,
                YCWA = YCWA,
                Y_cnc_b = YCWA + 50,
                XC = (XRY + L) // 2,
                c =  round( (win_inner_width - 756) / 2) + L,
                my = round( (win_inner_height - 185) / 2 + 80) + T
                )

    def _set_setting(self, what, mp: Tuple[int, int]):
        s = self.sizes
        if what == "window_title_height":
            self.window_title_height = mp[1]
        elif what == "window_title_height_plus_menu":
            self.window_title_height_plus_menu = mp[1]
        elif what == "advertising_area_top":
            self.advertising_area_top = s.H - mp[1]
        elif what == "tab_width":
            self.tab_width = s.W - mp[0]
        elif what == "tab_Programm_y":
            self.tab_Programm_y = mp[1]
        elif what == "tab_Einrichten_y":
            self.tab_Einrichten_y = mp[1]
        elif what == "speed_pos_continuous_xy":
            self.speed_pos_continuous_xy = (mp[0], mp[1] - s.win_inner_height)
        elif what == "speed_pos_0_01_xy":
            self.speed_pos_0_01_xy = (mp[0], mp[1] - s.win_inner_height)
        else:
            raise Exception(f"don't know how to set setting {what}")


    def setup(self):
        with WithWindow(self.match_beamicon_main) as bw:
            keys = iter(BeamiconSettings_configurable.keys())
            key = None
            def describe_next():
                nonlocal key, keys
                try:
                    key = next(keys)
                    print(f"configuring {key}. {BeamiconSettings_configurable[key]}. Then press F1")

                except StopIteration:
                    key = None
                    with CONFIG_FILE.open('w') as f:
                        f.write(beamicon_settings.to_json())
                    print(f" config file {CONFIG_FILE} written. You're done. Let's hope it works :-)")

            describe_next()

            def next_():
                mp = ahk.get_mouse_pos()
                print(f"mp {mp}")
                self._set_setting(key, mp)
                describe_next()

            ahk.hotkey("F1", next_)



@dataclass
class Beamicon:

    settings: BeamiconSettings

    @property
    def sizes(self):
        return self.settings.sizes

    @with_beamicon_main_window
    def goto_reference(self):
        self.beamicon_select_tab("Einrichten")
        s = self.sizes
        click_rel_window( s.XC, 354 - s.T)

    @with_beamicon_main_window
    def beamicon_select_tab(self, tab: Literal["Programm", "Einrichten"]):
        # WinGetPos, X, Y, W, H, A
        s = self.sizes
        mx = s.XRTY-15

        if (tab == "Programm"):
            click_rel_window(mx, s.T +  20)

        if (tab == "Einrichten"):
            click_rel_window( mx, s.T + 80)
        time.sleep(0.2) # 0.2 worked ?

    @with_beamicon_main_window
    def SetSpeed(self, speed):
        s = self.sizes
        self.beamicon_select_tab( "Einrichten")
        click_rel_window( s.L + 200, s.T + speed + -18 )

    @with_beamicon_main_window
    def x_axis_set_0(self):
        s = self.sizes
        self.beamicon_select_tab( "Einrichten")
        mx = s.XRY - minus_x_zero_buttons
        click_rel_window( mx, s.T + zero_x + 0 * zero_d )

    @with_beamicon_main_window
    def y_axis_set_0(self):
        s = self.settings.sizes
        self.beamicon_select_tab( "Einrichten")
        mx = s.XRY - minus_x_zero_buttons
        click_rel_window( mx, s.T + zero_x + 1 * zero_d )

    @with_beamicon_main_window
    def z_axis_set_0(self):
        s = self.sizes
        self.beamicon_select_tab( "Einrichten")
        mx = s.XRY - minus_x_zero_buttons
        click_rel_window( mx, s.T + zero_x + 2 * zero_d  )

    @with_beamicon_main_window
    def all_axis_set_0(self):
        s = self.sizes
        self.beamicon_select_tab( "Einrichten")
        mx = s.XRY - minus_x_zero_buttons
        click_rel_window( mx, s.T + zero_x + 4 * zero_d  )

        # my = round( (H - 185) / 2 + 80)
        # c  = round( (W - 756) / 2)
        # C  = round( (W - 28) / 2) # real center

    @with_beamicon_main_window
    def program_reset(self):
        s = self.sizes
        self.beamicon_select_tab( "Programm")
        mx = s.c + -30
        click_rel_window( mx, s.Y_cnc_b )

    @with_beamicon_main_window
    def stop(self):
        s = self.sizes
        mx = s.c + 20
        self.beamicon_select_tab("Programm")
        click_rel_window( mx, s.Y_cnc_b)

    @with_beamicon_main_window
    def play(self):
        s = self.sizes
        mx = s.c - 160
        self.beamicon_select_tab( "Programm")
        click_rel_window( mx, s.Y_cnc_b)

    @with_beamicon_main_window
    def MDI(self, mdi: str):
        """ gcode for movement """
        s = self.sizes
        C = s.XC
        my = round( s.YCWA / 2 + 80)

        self.beamicon_select_tab( "Einrichten")
        click_rel_window( C+48, s.T+ 100 )

        with WithWindow(self.settings.match_beamicon_MDI) as bw:
            ahk.send("^a")
            cp.copy(mdi)
            ahk.send("^v")
            ahk.send("{Enter}")
            # mdi.close()

    def machine_coordinates(self):
        global pos_ys

        s = self.sizes
        # pixels to top of X/Y/Z positions inputs
        X = s.XRY - 235

        # drop down 235 / 300
        # X 60px
        # Z 281
        self.beamicon_select_tab( "Einrichten")

        # select machine coordinates
        # click_rel_window(W - 235, 300 + YP)
        # ahk.send("{Pos1}")

        def v(Y):
            nonlocal X
            click_rel_window(X, Y)
            cp.copy("ABC")
            ahk.send("{POS1}{LSHIFT DOWN}{END}{LSHIFT UP}^c")
            time.sleep(0.05)
            # raise Exception("a")
            number = cp.paste()
            print("got value %s" % str(number))
            assert len(number) > 2 
            assert number != "ABC"
            return float(number)

        r = np.array([ v(y + s.T) for y in pos_ys])
        print(r)
        return r

    def setup_external_keyboard(self):
        for key in "Down Up Left Right PgUp PgDn".split(" "):
            def down():
                ahk.send("{%s Down}" % key)
            def up():
                ahk.send("{%s Up}" % key)
            ahk.hotkey("Numpad" + key, down)
            ahk.hotkey("Numpad" + key + " Up", up )

        for x in [
        ["Numpad5", lambda: self.goto_reference()],
        # ["Numpad0", all_axis_set_to_0],
        ["Numpad7", lambda: self.x_axis_set_0()],
        ["Numpad8", lambda: self.y_axis_set_0()],
        ["Numpad9", lambda: self.z_axis_set_0()],
        ["NumpadDot", lambda: self.goto_reference()],
        ["Numpad4", lambda: self.program_reset()],
        ["Numpad5", lambda: self.stop()],
        ["Numpad6", lambda: self.play()],

        ["NumpadDiv",   lambda: self.SetSpeed(speeds["continuous"])],
        ["NumpadMult",  lambda: self.SetSpeed(speeds["10 mm"])],
        ["NumpadMult",  lambda: self.SetSpeed(speeds["1 mm"])],
        ["NumpadAdd",   lambda: self.SetSpeed(speeds["0.1 mm"])],
        ["NumpadEnter", lambda: self.SetSpeed(speeds["0.01 mm"])]

        ]:
            ahk.hotkey(x[0], x[1]) # 3rd arg addiotional arguments
        return """
        ; Menü muss weg sein !!
        ;
        ; Nummern Block rechts:
        ;
        ; NumLock aus:
        ;   / * - + return -> Geschwindigkeit
        ;   Pfeiltasten + BildHoch/Runter -> bewegen

        ; NumLock aktiv
        ;   7 = x auf 0
        ;   8 = y auf 0
        ;   9 = z auf 0
        ;   , = zu Referenzpunkt fahren
        ;   4 (pfeil links)  = first command of program
        ;   5                = stop
        ;   6 (pfeil rechts) = play

        """

    @with_beamicon_main_window
    def move_mouse_to(self, x, y):
        s = self.sizes
        if (x<0):
            assert(False) # when is this used ? might not be very accurate because tab size might depend on font size
            x =  s.W + x
        ahk.mouse_move(x=x, y=y+s.T, relative_to="window")

beamicon_settings = BeamiconSettings.from_config_file()
beamicon = Beamicon(beamicon_settings);

# beamicon.start/stop etc see above



# # @ahk.hotkey("F1")
# def bye():
#     ahk.message_box("Bye!")
#     sys.exit()
# 
# ahk.hotkey("F1", bye)
