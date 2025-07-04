from fabric.widgets.label import Label
from fabric.core.service import Service, Signal
from fabric.widgets.button import Button
from fabric.utils import (
    invoke_repeater,
)
import psutil
import pulsectl
import math
import fontawesome as fa

class SoundService(Service):
    @Signal 
    def bat_changed(self, new_bat : int) -> None:
        self.change()
    
    @Signal
    def bat_logo_changed(self, new_logo : str) -> None:
        self.change()

    @Signal
    def change(self) -> None:...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pulse = pulsectl.Pulse('volume-reader')
        self.percent = 10000
        self.logo = ""
        self.mute = False
        self.time_to_empty = 0
        self.is_plugged = False
        invoke_repeater(100, self.update_values)


    def update_values(self):
        pulse = self.pulse 
        default_sink_name = pulse.server_info().default_sink_name

        default_sink = None
        for sink in pulse.sink_list():
            if sink.name == default_sink_name:
                default_sink = sink
                break

        sink = default_sink
        new_snd_lev = math.floor(sink.volume.values[0]*100)
        is_muted = sink.mute
        if new_snd_lev!= self.percent or self.mute!=is_muted:
            self.percent = new_snd_lev
            self.bat_changed(new_snd_lev)

            if new_snd_lev > 74:
                new_snd_logo = "\uf028"

            elif new_snd_lev > 24:
                new_snd_logo =  "\uf027"
            else:
                new_snd_logo = "\uf026"

            if is_muted:
                new_snd_logo="\uf6a9"
            self.mute=is_muted

            if new_snd_logo != self.logo :
                self.logo=new_snd_logo
                self.bat_logo_changed(new_snd_logo)
        
        
        return True

    

class SoundWidget(Button):
    def on_click(self, button):
        self.full = not self.full
        self.update_bat()

    def __init__(self, **kwargs):
        super().__init__(name="hyprland-window",**kwargs)
         
        self.sound = SoundService()
        self.full = False
        
        self.connect("clicked", self.on_click)

        self.add(Label(""))

        self.sound.connect(
            "bat_changed",
            lambda _, new_bat: self.update_bat()
        )

        self.sound.connect(
            "change",
            lambda _: self.update_bat()
        )
        self.update_bat()

 
    def update_bat(self):
        self.children[0].set_label(self.sound.logo 
            + f" {str(self.sound.percent)+"%" if self.full else ""}" 
        )
        self.children[0].set_has_tooltip(False)


