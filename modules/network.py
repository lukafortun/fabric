from fabric.widgets.label import Label
from fabric.core.service import Service, Signal
from fabric.widgets.button import Button
from fabric.utils import (
    invoke_repeater,
)
import subprocess

class NetworkService(Service):

    @Signal 
    def net_changed(self ) -> None:
        print(f"network changed : {self}")
        self.change()

    @Signal
    def net_list_changed(self, new_logo : str) -> None:
        self.change()

    @Signal
    def change(self) -> None:...


    def __init__(self, interface=None, **kwargs):
        super().__init__(**kwargs)
        self.interface = interface or self.get_default_interface()
        self.connected = False
        self.ssid = None
        self.signal = None
        self.connection_type = 'none'
        self.internet = False
        self.logo = None
        self.percent = 0 
        
        self.update_current()
        invoke_repeater(3000, self.update_current)
    

    def update_current(self):
        interface = self.get_default_interface()
        connected, ssid = self.get_active_connection()
        signal = self.get_current_wifi_signal()
        connection_type = self.get_connection_type()
        internet = self.is_internet_connected()

        
        match connection_type:
            case "ethernet":
                logo = "\uf796"
            case "wifi":
                logo = "\uf1eb"
            case _:
                logo = "\uf05e"
        if logo!=self.logo or connected!=self.connected or ssid!=self.ssid or self.signal!=signal or self.connection_type!=connection_type or internet!=self.internet:
            self.interface = interface
            self.connected = connected
            self.ssid = ssid
            self.signal = signal
            self.connection_type = connection_type
            self.internet = internet
            self.logo = logo
            self.net_changed()



        return True

    def update_list(self):
        return

    def get_default_interface(self):
        cmd = "LC_ALL=C nmcli -t -f DEVICE,TYPE,STATE dev"
        result = subprocess.getoutput(cmd).strip().splitlines()

        for line in result:
            parts = line.split(":")
            if len(parts) >= 3:
                device, type_, state = parts
                if state == 'connected' and (type_ == 'wifi' or type_ == 'ethernet'):
                    return device
        return 'wlan0'


    def get_active_connection(self):
        cmd = f"LC_ALL=C nmcli -t -f GENERAL.CONNECTION dev show {self.interface}"
        result = subprocess.getoutput(cmd).strip()
        if result.startswith("GENERAL.CONNECTION:"):
            ssid = result.split(":", 1)[1].strip()
            return bool(ssid), ssid if ssid else None
        return False, None

    def get_current_wifi_signal(self):
        try:
            result = subprocess.getoutput("cat /proc/net/wireless").splitlines()
            for line in result:
                if self.interface in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        signal_raw = float(parts[2].strip('.')) 
                        signal_percent = int((signal_raw / 70) * 100)
                        return min(max(signal_percent, 0), 100)
            return None
        except Exception:
            return None

    def get_connection_type(self):
        cmd = "LC_ALL=C nmcli -t -f DEVICE,TYPE,STATE dev"
        result = subprocess.getoutput(cmd).strip().splitlines()

        for line in result:
            parts = line.split(":")
            if len(parts) >= 3:
                device, type_, state = parts
                if device == self.interface and state == 'connected':
                    return type_
        return 'none'

    def is_internet_connected(self):
        try:
            subprocess.check_output(["ping", "-c", "1", "-W", "1", "8.8.8.8"], stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False

    def scan_wifi_networks(self):
        cmd = f"LC_ALL=C nmcli -t -f in-use,ssid,signal,security dev wifi"
        result = subprocess.getoutput(cmd).strip().splitlines()

        networks = []
        for line in result:
            parts = line.split(":")
            if len(parts) >= 4:
                in_use, ssid, signal, security = parts
                if ssid:
                    networks.append({
                        'ssid': ssid,
                        'signal': int(signal) if signal.isdigit() else 0,
                        'security': security if security else 'Open',
                        'active': in_use.strip() == '*'
                    })
        return networks

    def get_wifi_security_type(self, ssid):
        networks = self.scan_wifi_networks()
        for net in networks:
            if net['ssid'] == ssid:
                sec = net['security'].lower()
                if not sec or sec == '--':
                    return 'open'
                elif '802.1x' in sec:
                    return 'enterprise'
                else:
                    return 'password'
        return None

    def connect_to_wifi(self, ssid, password=None, username=None):
        security_type = self.get_wifi_security_type(ssid)

        if security_type == 'open':
            cmd = f"nmcli dev wifi connect '{ssid}'"
        elif security_type == 'password' and password:
            cmd = f"nmcli dev wifi connect '{ssid}' password '{password}'"
        elif security_type == 'enterprise' and username and password:
            cmd = f"nmcli dev wifi connect '{ssid}' password '{password}' 802-1x.identity '{username}'"
        else:
            return False, f"Informations manquantes pour se connecter à '{ssid}' ({security_type})"

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
            return True, output.strip()
        except subprocess.CalledProcessError as e:
            return False, e.output.strip()

    def as_dict(self):
        return {
            'connected': self.connected,
            'ssid': self.ssid,
            'signal': self.signal,
            'connection_type': self.connection_type,
            'internet': self.internet
        }

    def __str__(self):
        status = f"Type: {self.connection_type}, "
        if self.connection_type == 'wifi' and self.connected:
            status += f"SSID: {self.ssid}, Signal: {self.signal}%, "
        status += f"Internet: {'Oui' if self.internet else 'Non'}"
        return status



