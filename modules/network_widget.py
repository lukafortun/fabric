from pywifi import PyWiFi, const, Profile
import nmcli



class NetworkService(Service):
    @Signal 
    def network_changed(self, new_net : str) -> None:
        self.change()
    
    @Signal
    def power_changed(self, new_power : int) -> None:
        self.change()

    @Signal
    def connection_changed(self, new_state: bool) -> None:
        self.change()

    @Signal 
    def time_to_empty_changed(self, new_time: int) -> None:
        self.change()

    @Signal
    def change(self) -> None:...

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


        
        invoke_repeater(5000, self.update_values)

    def get_sig_quality(self, signal : int)->int:
        if signal >= -50:
            return 3
        elif -60 <= signal < -50:
            return 2
        elif -70 <= signal < -60:
            return 1
        else:
            return 0 

    def update_values(self):
        self.iface.scan()
        self.results = self.iface.scan_results()


        
        self.connected = (self.iface.status() == const.IFACE_CONNECTED)
        if self.connected:
            self.ssid = self.iface.network_profile[0].ssid
       
        network = next((net for net in self.results if net.ssid == self.ssid), None)
        self.power = get_sig_quality(network.signal)
        self.change()
        return True

class NetworkWidget(Box):

    def __init__(self, **kwargs):
        super().__init__(name="hyprland-window",**kwargs)
         
        self.network = NetworkService()
        
        self.add(Label(""))


        self.network.connect(
            "change",
            lambda _: self.update_bat()
        )

        self.update_bat()

 
    def update_bat(self):
        self.children[0].set_label(self.network.power +" "+ str(self.network.ssid))  

