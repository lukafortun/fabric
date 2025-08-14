from modules.battery_widget import BatteryWidget
from modules.sound_widget import SoundWidget
from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.datetime import DateTime
from fabric.widgets.centerbox import CenterBox
from fabric.system_tray.widgets import SystemTray
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.hyprland.widgets import Language, ActiveWindow, Workspaces, WorkspaceButton
from fabric.widgets.button import Button
from fabric.utils import (
    FormattedString,
    bulk_replace,
)
from gi.repository import GLib, Gdk
from utils.svg_utils import recolor_svgfile_env
from modules.network_widget import NetworkWidget
from modules.network import NetworkService

class Logo(Button):
    def __init__(self, **kwargs):
        super().__init__(name="logo-box", **kwargs)
        logo = "assets/nerv.svg"
        self.logo = Svg(svg_string=recolor_svgfile_env(logo, "COLOR_PRIMARY"), name="logo", size=20, style_classes="main-logo")
        self.add(self.logo)


class Bar(Window):
    def showmenu(self, widget): 
        self.power_menu.toggle_visibility()


    def keypressed(self, widget, event):
        print('hello' + str(event.keyval))
        # match event.keyval:
            # case Gdk.KEY_Super_L: 
            #     self.power_menu.toggle_visibility()
            # case Gdk.KEY_Super_R:
            #     self.power_menu.toggle_visibility()

    def __init__(
        self,
        power_menu,
    ):
        super().__init__(
            name="bar",
            layer="top",
            anchor="left top right",
            margin="0px 0px -2px 0px",
            exclusivity="auto",
            visible=False,
            all_visible=False,
            on_key_release_event=self.keypressed,
            keyboard_mode="on-demand"
        )
        


        self.power_menu = power_menu


        self.logo = Logo()
        
        self.logo.connect("clicked", self.showmenu)

        
        self.workspaces = Workspaces(
            name="workspaces",
            spacing=4,
            # buttons_factory=lambda ws_id: WorkspaceButton(id=ws_id, label=None),
            buttons=[WorkspaceButton(id=i, label=None) for i in range(1, 11)],
        )
        self.active_window = ActiveWindow(name="hyprland-window")
        self.language = Language(
            formatter=FormattedString(
                "{replace_lang(language)}",
                replace_lang=lambda lang: bulk_replace(
                    lang,
                    (r".*Eng.*", r".*Ar.*", r".*Fr.*"),
                    ("ENG", "ARA", "FRA"),
                    regex=True,
                ),
            ),
            name="hyprland-window",
        )
        self.date_time = DateTime(name="date-time")
        self.system_tray = SystemTray(name="system-tray", spacing=4, icon_size=16)






        self.network_service = NetworkService()
        self.test_bat = BatteryWidget()
        self.test_snd = SoundWidget()
        self.test_net = NetworkWidget(self.network_service)

        self.button = Button(name="hyprtask")
       
        self.center = Box(name="control-center",
                          children=[
                            self.test_bat,
                            self.test_snd,
                            self.test_net
                          ])

        self.children = CenterBox(
            name="bar-inner",
            start_children=Box(
                name="start-container",
                spacing=4,
                orientation="h",
                children=[
                    self.logo,
                    self.workspaces,      
                          ]
            ),
            center_children=Box(
                name="center-container",
                spacing=4,
                orientation="h",
                children=self.active_window,
            ),
            end_children=Box(
                name="end-container",
                spacing=4,
                orientation="h",
                children=[
                    # self.status_container,
                    self.system_tray,
                    self.center,
                    self.date_time,
                    self.language,
                    self.button,
                ],
            ),
        )


        self.show_all()



