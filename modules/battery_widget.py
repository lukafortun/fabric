from fabric.widgets.label import Label
from fabric.core.service import Service, Signal
from fabric.widgets.button import Button
from fabric.utils import (
    invoke_repeater,
)
import psutil


class BatteryService(Service):
    @Signal 
    def bat_changed(self, new_bat : int) -> None:
        self.change()
    
    @Signal
    def bat_logo_changed(self, new_logo : str) -> None:
        self.change()

    @Signal
    def is_plugged_changed(self, new_state: bool) -> None:
        self.change()

    @Signal 
    def time_to_empty_changed(self, new_time: int) -> None:
        self.change()

    @Signal
    def change(self) -> None:...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.percent = 0
        self.logo = ""
        self.time_to_empty = 0
        self.is_plugged = False
        invoke_repeater(5000, self.update_values)


    def update_values(self):
        battery = psutil.sensors_battery()
        new_bat_lev = int(battery.percent)
        if new_bat_lev!= self.percent :
            self.percent = new_bat_lev
            print("change")
            self.bat_changed(new_bat_lev)

            if new_bat_lev >= 100:
                new_bat_logo = "\uf240"
            elif new_bat_lev > 74:
                new_bat_logo = "\uf241"

            elif new_bat_lev > 49:
                new_bat_logo = "\uf242"
            elif new_bat_lev > 24:
                new_bat_logo =  "\uf243"
            else:
                new_bat_logo = "\uf244"
            
            if new_bat_logo != self.logo :
                self.logo=new_bat_logo
                self.bat_logo_changed(new_bat_logo)

        
        new_time_to_empty = battery.secsleft
        if new_time_to_empty != self.time_to_empty:
            self.time_to_empty = new_time_to_empty
            self.time_to_empty_changed(new_time_to_empty)

        new_is_plugged = battery.power_plugged
        if new_is_plugged != self.is_plugged:
            self.is_plugged = new_is_plugged
            self.is_plugged_changed(new_is_plugged)
        
        return True

    

class BatteryWidget(Button):

    def __init__(self, **kwargs):
        super().__init__(name="hyprland-window",**kwargs)
         
        self.battery = BatteryService()
        
        self.add(Label(""))

        self.battery.connect(
            "bat_changed",
            lambda _, new_bat: self.update_bat()
        )

        self.battery.connect(
            "change",
            lambda _: self.update_bat()
        )

        self.update_bat()

 
    def update_bat(self):
        self.children[0].set_label(self.battery.logo +" "+ str(self.battery.percent)+"%" + ("\uf0e7" if self.battery.is_plugged else ""))
        if not(self.battery.is_plugged):
            self.children[0].set_markup
            self.children[0].set_has_tooltip(True)
            minutes = self.battery.time_to_empty //60 %60
            hours = self.battery.time_to_empty //60
            self.children[0].set_tooltip_text(f"Time to empty : {hours}h {minutes}m")
        else:
            self.children[0].set_has_tooltip(False)


