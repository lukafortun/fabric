#!../fabric-venv/bin/python3
from modules.bar import Bar
from modules.power_menu import PowerMenu
from utils.socket_listener import SocketListener
from fabric import Application
from utils.css_generator import generate_css_variables_from_env
from fabric.utils import (
    get_relative_path,
)


if __name__ == "__main__":
    socket_listener = SocketListener()


    pm = PowerMenu()
    bar = Bar(pm)
    app = Application("bar", bar,pm)
    generate_css_variables_from_env()

    app.set_stylesheet_from_file(get_relative_path("stylesheets/main.css"))

    socket_listener.add_command("toggle_power_menu", pm.toggle_visibility)
    socket_listener.add_command("toggle_power_button", pm.toggle_menu_button)
    socket_listener.start()

    app.run()
