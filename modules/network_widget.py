from fabric.widgets.label import Label
from fabric.core.service import Service, Signal
from fabric.widgets.button import Button
from fabric.utils import (
    invoke_repeater,
)
from modules.network import NetworkService
import math

    

class NetworkWidget(Button):
    def on_click(self, button):
        self.full = not self.full
        self.update_net()

    def __init__(self, networkService,**kwargs):
        super().__init__(name="net",**kwargs)
         
        self.network = networkService
        self.full = False
        
        self.connect("clicked", self.on_click)

        self.add(Label(""))

        self.network.connect(
            "net_changed",
            lambda _: self.update_net()
        )

        self.update_net()


    def update_net(self):
        self.children[0].set_label(self.network.logo 
            + f"{" "+str(self.network.ssid) if self.full else ""}" 
        )
        self.children[0].set_tooltip_text(f"Signal power : {self.network.signal}%\nSSID : {self.network.ssid}")



