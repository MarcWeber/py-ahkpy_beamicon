import sys
from dataclasses_json import dataclass_json
import numpy as np
import traceback
import warnings
import math
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

# each of these settinsg can be set by mouse
# see set_*
BeamiconSettings_configurable = {

        "window_title_height": "moandve your mouse at the bottom of the window title bar to estimate its height",
        "window_title_height_plus_menu": "move your mouse at the bottom of the menu / navigation bar within beamicon to estimate its heighth",
        "window_title_height_plus_toolbar": "move your mouse at the bottom of the menu / navigation bar within beamicon to estimate its heighth",

        "tab_width": "lefth side of the tab bar on the rigth end of the window",
        "tab_Programm_y": "center of the tab Programm",
        "tab_Einrichten_y": "center of the tab Einrichten",

        "advertising_area_height": "",


        # tab program buttons R64958172
        "play_xy": "start button on tab Programm",
        "n_xy": "stop button on tab Programm",
        "rewind_xy": "gcode rewind button on tab Programm",
        "stop_xy": "stop button",
        "edit_file_xy": "open gcode file",
        "edit_xy": "edit_xy",


        # tab Jog/Setup / Einrichten buttons R3127775242
        "topleft_xy": "center of topleft button on second tab (the following are ",
        "top_xy": "center of top button on second tab",
        "topright_xy": "center of topright button on second tab",
        "zup_xy": "center of up button on second tab",
        "left_xy": "center of left button on second tab",
        "right_xy": "center of right button on second tab",
        "downleft_xy": "center of downleft button on second tab",
        "down_xy": "center of down button on second tab",
        "downright_xy": "center of downright button on second tab",
        "zdown_xy": "center of zdown button on second tab",


        "speed_pos_continuous_xy": "", # of drop down's first
        "speed_pos_0_01_xy": "",       # of drop down's last


        "x0_xy": "center of x[0] button top right",
        "y0_xy": "center of y[0] button top right",
        "z0_xy": "center of z[0] button top right",
        "xyz0_xy": "center of xyz[0] button top right",
}

SettingKey: TypeAlias = Literal[


        "window_title_height",
        "window_title_height_plus_menu",
        "window_title_height_plus_toolbar",

        "tab_width",
        "tab_Programm_y",
        "tab_Einrichten_y",

        "advertising_area_height",


        # tab program buttons R64958172
        "play_xy",
        "n_xy",
        "rewind_xy",
        "stop_xy",
        "edit_file_xy",
        "edit_xy",


        # tab Jog/Setup / Einrichten buttons R3127775242
        "topleft_xy",
        "top_xy",
        "topright_xy",
        "zup_xy",
        "left_xy",
        "right_xy",
        "downleft_xy",
        "down_xy",
        "downright_xy",
        "zdown_xy",


        "speed_pos_continuous_xy",
        "speed_pos_0_01_xy",


        "x0_xy",
        "y0_xy",
        "z0_xy",
        "xyz0_xy",
]

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
    program_button_center: Tuple[int, int]
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
    window_title_height_plus_toolbar: int = 60

    tab_width: int =30
    tab_Programm_y: int = 40
    tab_Einrichten_y: int = 40


    advertising_area_height: int = 80


    # program tab buttons R64958172
    # R4114271535
    # the location is complicatde
    # removing and and tabs
    # left half
    # bottom half
    # y: some pixels down
    # x: center + some pixels 
    play_xy: Tuple[int, int] = (0,0)
    n_xy: Tuple[int, int] = (0,0)
    rewind_xy: Tuple[int, int] = (0,0)
    stop_xy: Tuple[int, int] = (0,0)
    edit_file_xy: Tuple[int, int] = (0,0)
    edit_xy: Tuple[int, int] = (0,0)



    # Jog/Setup buttons R3127775242
    topleft_xy: Tuple[int, int] = (0,0)
    top_xy: Tuple[int, int] = (0,0) # R696427638
    topright_xy: Tuple[int, int] = (0,0)
    zup_xy: Tuple[int, int] = (0,0) # R696427638
    left_xy: Tuple[int, int] = (0,0) # R696427638
    right_xy: Tuple[int, int] = (0,0) # R696427638
    downleft_xy: Tuple[int, int] = (0,0)
    down_xy: Tuple[int, int] = (0,0) # R696427638
    downright_xy: Tuple[int, int] = (0,0)
    zdown_xy: Tuple[int, int] = (0,0) # R696427638

    speed_pos_continuous_xy: Tuple[int, int] = (0,0) # y counting from #inner_window
    speed_pos_0_01_xy:       Tuple[int, int] = (0,0) # y counting from #inner_window


    # R696427638: keys can be used button doesn't have to be clicked
    # but clicking buttnos from left right top down is faster than thinkng a lot ..
    # so let's keep all settings for now


    @staticmethod
    def from_config_file() -> Tuple[bool, 'BeamiconSettings']:
        if not CONFIG_FILE.exists():
            bs = BeamiconSettings.from_dict(settings_defaults)
            print("BeamiconSettings not setup yet, starting setup(). Please follow instructions")
            return True, bs
        else:
            with CONFIG_FILE.open('r') as f:
                bs = BeamiconSettings.from_json(f.read())
            print(f"settinsg example left_xy={bs.left_xy}")
            return False, bs
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
        T = self.window_title_height_plus_toolbar if self.TOOLBAR_ACTIVE else self.window_title_height_plus_menu
        bw = WithWindow.current()

        X, Y, W, H = bw.x, bw.y, cast(int, bw.width), bw.height
        if (bw.is_maximized):
            R, L = 0, 0
        else:
            R, L = SHADOW_LR

        # The inner window
        # remove tabs on right
        # remove menu top if its active
        # remove ads bottom
        # content is layout within this box

        border_left = 4
        inner_rect_topleft  = np.array([4, T], dtype=np.int32)
        inner_rect_size     = np.array([W ,H - T - self.advertising_area_height ], dtype=np.int32)
        center = inner_rect_size / 2
        program_button_center = (center[0]/2, center[1])


        # 25 tab width, should be taken from settings
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
                program_button_center = program_button_center,
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

    def setting_from_mouse_pos(self, what: SettingKey, mp: Tuple[int, int]):
        s = self.sizes
        if what == "window_title_height":
            self.window_title_height = mp[1]
        elif what == "window_title_height_plus_menu":
            self.window_title_height_plus_menu = mp[1]
        elif what == "window_title_height_plus_toolbar":
            self.window_title_height_plus_toolbar = mp[1]
        elif what == "advertising_area_height":
            self.advertising_area_height = s.H - mp[1]
        elif what == "tab_width":
            self.tab_width = s.W - mp[0]
        elif what in [ "tab_Einrichten_y", "tab_Programm_y"]:
            setattr(self, what, mp[1] - s.T)
        elif what in ["x0_xy", "y0_xy", "z0_xy", "xyz0_xy"]:
            setattr(self, what, (mp[0] - s.L, mp[1] - s.T))
        elif what in ["speed_pos_continuous_xy", "speed_pos_0_01_xy"]:
            setattr(self, what, (mp[0] - s.L, mp[1] - s.T))
        elif what in ["topleft_xy", "top_xy", "topright_xy", "zup_xy", "left_xy", "right_xy", "downleft_xy", "down_xy", "downright_xy", "zdown_xy"]:
            setattr(self, what, (mp[0] - s.L, mp[1] - s.T))
        elif what in [ "play_xy", "n_xy", "rewind_xy", "stop_xy", "edit_file_xy", "edit_xy" ]:
            C = s.program_button_center
            # R4114271535
            setattr(self, what, (mp[0] - C[0], mp[1] - C[1]))
        else:
            raise Exception(f"don't know how to set setting {what}")

    def mouse_pos_from_setting(self, what: SettingKey):
        s = self.sizes
        v = getattr(self, what)
        if what == "window_title_height":
            mp = (100, v)
        elif what == "window_title_height_plus_menu":
            mp = (100, v)
        elif what == "window_title_height_plus_toolbar":
            mp = (100, v)
        elif what == "advertising_area_height":
            mp = (100, s.H - v)
        elif what == "tab_width":
            mp = (s.W - self.tab_width, 130)
        elif what in [ "tab_Einrichten_y", "tab_Programm_y"]:
            mp = (s.W - 15, s.T + v)
        elif what in ["x0_xy", "y0_xy", "z0_xy", "xyz0_xy"]:
            mp = (s.L + v[0], s.T + v[1])
        elif what in ["speed_pos_continuous_xy", "speed_pos_0_01_xy"]:
            mp = (s.L + v[0], s.T + v[1])
        elif what in ["height", "top_xy", "topright_xy", "zup_xy", "left_xy", "right_xy", "downleft_xy", "down_xy", "downright_xy", "zdown_xy"]:
            mp = (s.L + v[0], s.T + v[1])
        elif what in [ "play_xy", "n_xy", "rewind_xy", "stop_xy", "edit_file_xy", "edit_xy" ]:
            C = s.program_button_center
            # R4114271535
            mp = (C[0] + v[0], C[1] + v[1])
        else:
            raise Exception(f"don't know how to set setting {what}")
        return mp


@dataclass
class Beamicon:

    settings: BeamiconSettings

    tab: str | None = None # last selected tab

    @property
    def sizes(self):
        return self.settings.sizes


    def settings_from_mouse_pos(self, missing_only = False, move_mouse = True):
        """
        guides the user to press F1 on the location
        to get x/y coordinates of the points of interest
        """
        with WithWindow(self.settings.match_beamicon_main) as bw:
            keys = iter([k for k in BeamiconSettings_configurable.keys() if not hasattr(self, k)] if missing_only else BeamiconSettings_configurable.keys())
            key = None

            def write():
                with CONFIG_FILE.open('w') as f:
                    f.write(self.settings.to_json())

            def describe_next():
                nonlocal key, keys
                try:
                    key = next(keys)
                    if key == "play_xy":
                        self.beamicon_select_tab("Programm")
                    if key == "topleft_xy":
                        self.beamicon_select_tab("Einrichten")
                    if move_mouse:
                        try:
                            mp = self.settings.mouse_pos_from_setting(key)
                            if mp[0] != 0 and mp[1] != 0:
                                self.mouse_move_abs(*mp)
                        except:
                            print("ERROR SETTING MOUSE - maybe setting missing")
                            traceback.print_exc()

                    print(f"configuring {key}. {BeamiconSettings_configurable[key]}. Then press F1")

                except StopIteration:
                    key = None
                    write()
                    print(f" config file {CONFIG_FILE} written. You're done. Let's hope it works :-)")

            describe_next()

            def next_():
                mp = ahk.get_mouse_pos()
                print(f"mp {mp}")
                self.settings.setting_from_mouse_pos(key, mp)
                describe_next()
                write()

            ahk.hotkey("F1", next_)



    @with_beamicon_main_window
    def mouse_move_abs(self, x: float, y: float):
        print("moving %s " % str((x,y)))
        s = self.sizes
        ahk.mouse_move(x=x, y=y, relative_to="window")

    @with_beamicon_main_window
    def action_on_setting(self, setting: SettingKey, action: Literal["mouse_press", "mouse_release", "click"]):
        mp = self.settings.mouse_pos_from_setting(setting)
        self.mouse_move_abs(*mp)
        if action in ["click", "mouse_press", "mouse_release"]:
            getattr(ahk, action)()

    @with_beamicon_main_window
    def click_rel_window(self, x: float, y: float):
        warnings.warn("use action_on_setting", DeprecationWarning )
        self.mouse_move_abs(x, y)
        ahk.click()


    @with_beamicon_main_window
    def click_program_button(self, button: Literal[ "play", "n", "rewind", "stop", "edit_file", "edit" ]):
        warnings.warn("use action_on_setting", DeprecationWarning )
        self.beamicon_select_tab("Programm")
        self.action_on_setting(f"{button}_xy", "click")


    @with_beamicon_main_window
    def goto_reference(self):
        # rewrite TODO -> new button positions
        self.beamicon_select_tab("Einrichten")
        s = self.sizes
        self.click_rel_window( s.XC, 354 - s.T)

    @with_beamicon_main_window
    def beamicon_select_tab(self, tab: Literal["Programm", "Einrichten"]):
        if self.tab == tab:
            return

        if tab == "Programm":
            y = self.settings.mouse_pos_from_setting("tab_Programm_y")
            self.action_on_setting("tab_Programm_y", action ="click")
            self.tab = tab

        if tab == "Einrichten":
            y = self.settings.mouse_pos_from_setting("tab_Einrichten_y")
            self.action_on_setting("tab_Einrichten_y", action ="click")
            self.tab = tab

        time.sleep(0.2) # 0.2 worked ? R3562056818

    @with_beamicon_main_window
    def SetSpeed(self, speed: Literal["continuous", "10 mm", "1 mm", "0.1 mm", "0.01 mm"]):
        print(f"setting speed {speed}")
        speeds = [ "continuous", "10 mm", "1 mm", "0.1 mm", "0.01 mm" ]
        idx = speeds.index(speed)
        s = self.sizes
        self.beamicon_select_tab( "Einrichten")
        self.click_rel_window(
            s.L + self.settings.speed_pos_continuous_xy[0],
            s.T + self.settings.speed_pos_continuous_xy[1]
            + round(1.0 * idx * (1.0 + self.settings.speed_pos_0_01_xy[1] - self.settings.speed_pos_continuous_xy[1]) / len(speeds))
        )


    @with_beamicon_main_window
    def axis_set_0(self, axis: Literal["x", "y", "z", "xyz"]):
        warnings.warn("use action_on_setting", DeprecationWarning )
        s = self.sizes
        attr = f"{axis}0_xy"
        v = getattr(self.settings, attr)
        self.click_rel_window( s.L + v[0], s.T + v[1])

    def x_axis_set_0(self):
        raise Exception('use axis_set_0')
    def y_axis_set_0(self):
        raise Exception('use axis_set_0')
    def z_axis_set_0(self):
        raise Exception('use axis_set_0')

    @with_beamicon_main_window
    def all_axis_set_0(self):
        raise Exception('use axis_set_0')

    @with_beamicon_main_window
    def program_reset(self):
        warnings.warn("use action_on_setting", DeprecationWarning )
        s = self.sizes
        self.beamicon_select_tab( "Programm")
        mx = s.c + -30
        self.click_rel_window( mx, s.Y_cnc_b )

    @with_beamicon_main_window
    def stop(self):
        warnings.warn("use action_on_setting", DeprecationWarning )
        s = self.sizes
        mx = s.c + 20
        self.beamicon_select_tab("Programm")
        self.click_rel_window( mx, s.Y_cnc_b)

    @with_beamicon_main_window
    def play(self):
        warnings.warn("use action_on_setting", DeprecationWarning )
        s = self.sizes
        mx = s.c - 160
        self.beamicon_select_tab( "Programm")
        self.click_rel_window( mx, s.Y_cnc_b)

    @with_beamicon_main_window
    def MDI(self, mdi: str):
        """ gcode for movement """
        s = self.sizes
        C = s.XC
        my = round( s.YCWA / 2 + 80)

        self.beamicon_select_tab( "Einrichten")
        self.click_rel_window( C+48, s.T+ 100 )

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
        # self.click_rel_window(W - 235, 300 + YP)
        # ahk.send("{Pos1}")

        def v(Y):
            nonlocal X
            self.click_rel_window(X, Y)
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

        mappings = [
            "NumpadPgDn:click:tab_Einrichten=downright_xy",
            "NumpadPgUp:click:tab_Einrichten=topright_xy",
            "NumpadHome:click:tab_Einrichten=topleft_xy",
            "NumpadEnd:click:tab_Einrichten=downleft_xy",


            "NumpadDown:click:tab_Einrichten=down_xy",
            "NumpadUp:click:tab_Einrichten=top_xy",
            "NumpadLeft:click:tab_Einrichten=left_xy",
            "NumpadRight:click:tab_Einrichten=right_xy",

            "NumpadIns:click:tab_Einrichten=zdown_xy",
            "NumpadDel:click:tab_Einrichten=zup_xy",


            # "NumpadDown:map:Up",
            # "NumpadUp:map:Up",
            # "NumpadLeft:map:Left",
            # "NumpadRight:map:Right",
            # "NumpadIns:map:PgDown",
            # "NumpadDel:map:PgUp",
        ]

        for map in mappings:
            key, action, x = map.split(':')
            if action == 'map':
                @with_beamicon_main_window
                def down():
                    ahk.send("{%s Down}" % x)
                    print("key is down")
                @with_beamicon_main_window
                def up():
                    ahk.send("{%s Up}" % x)
                    print("key is up")
                ahk.hotkey(key, down)
                ahk.hotkey(key + " Up", up )
            elif action == 'click':
                tab, button = x.split('=')

                @with_beamicon_main_window
                def down(tab, button):
                    s = self.settings.sizes
                    self.beamicon_select_tab(tab)
                    print(f"button {button}")
                    attr = getattr(self.settings, button)
                    print(f"attr {attr}")
                    self.mouse_move_abs(attr[0] + s.L, attr[1] + s.T)
                    ahk.mouse_press()
                    print("mouse is down")
                @with_beamicon_main_window
                def up(button):
                    ahk.mouse_release()
                    print("mouse is up")
                ahk.hotkey(key,         lambda tab=tab, button=button: down(tab[4:], button))
                ahk.hotkey(key + " Up", lambda button=button: up(button) )


        # for key in "Down Up Left Right PgUp PgDn Pos1".split(" "):
        #     ahk.mouse_move(x=x, y=y+T, relative_to="window")
        #     print("moving %s " % str((x,y)))
        #     ahk.click()
        #     ahk.hotkey(key, lambda: self.click())

        for x in [
            ["Numpad5", lambda: self.goto_reference()],
            # ["Numpad0", all_axis_set_to_0],
            ["Numpad7", lambda: self.axis_set_0("x")],
            ["Numpad8", lambda: self.axis_set_0("y")],
            ["Numpad9", lambda: self.axis_set_0("z")],
            ["NumpadDot", lambda: self.goto_reference()],
            ["Numpad4", lambda: self.click_program_button("rewind")],
            ["Numpad5", lambda: self.click_program_button("stop")],
            ["Numpad6", lambda: self.click_program_button("play")],

            ["NumpadDiv",   lambda: self.SetSpeed("continuous")],
            ["NumpadMult",  lambda: self.SetSpeed("10 mm")],
            ["NumpadSub",  lambda: self.SetSpeed("1 mm")],
            ["NumpadAdd",   lambda: self.SetSpeed("0.1 mm")],
            ["NumpadEnter", lambda: self.SetSpeed("0.01 mm")]

        ]:
            ahk.hotkey(x[0], x[1]) # 3rd arg addiotional arguments
        return """
        Menü muss weg sein !!

        Nummern Block rechts:

        NumLock aus:
          / * - + return -> Geschwindigkeit
          Pfeiltasten in xy Ebene bewegen auch diagonal!
          Numpad0: z-runter
          NumpadDot: z-rauf

        NumLock aktiv
          7 = x auf 0
          8 = y auf 0
          9 = z auf 0
          , = zu Referenzpunkt fahren
          4 (pfeil links)  = first command of program
          5                = stop
          6 (pfeil rechts) = play
        """


needs_setup, beamicon_settings = BeamiconSettings.from_config_file()
beamicon = Beamicon(beamicon_settings);
if needs_setup:
    beamicon.settings_from_mouse_pos()
# beamicon.settings_from_mouse_pos()

# beamicon.start/stop etc see above



# # @ahk.hotkey("F1")
# def bye():
#     ahk.message_box("Bye!")
#     sys.exit()
# 
# ahk.hotkey("F1", bye)
