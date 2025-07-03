from fabric.widgets.svg import Svg
from fabric.widgets.box import Box
from fabric.widgets.label import Label
from fabric.widgets.revealer import Revealer
from fabric.widgets.centerbox import CenterBox
from fabric.widgets.wayland import WaylandWindow as Window
from fabric.widgets.button import Button
from fabric.utils import get_desktop_applications, exec_shell_command_async
from fabric.widgets.image import Image
from fabric.widgets.scrolledwindow import ScrolledWindow
from fabric.widgets.entry import Entry
from gi.repository import GLib, Gdk



class PowerMenu(Window):
    

    class PowerButton(Box):
        def toggle(self):
            # self.revealer.set_transition_type(Gtk.RevealerTransitionType.SLIDE_LEFT)
            if self.active:
                # self.box.hide()
                self.revealer.set_reveal_child(False)
                # self.revealer.unreveal()
                self.powerbutton.children[0].set_from_file("assets/power.svg")
                self.powerbutton.get_style_context().remove_class("open")
            else:
                # self.box.show_all()
                self._all_apps = get_desktop_applications()
                self.revealer.set_reveal_child(True)
                # self.revealer.reveal()
                self.powerbutton.children[0].set_from_file("assets/close.svg")
                self.powerbutton.get_style_context().add_class("open")
            self.active = not(self.active)
            

        def __init__(self):
            super().__init__(name="power-rack")
            self.powerbutton = Button(name="power-button",
                                      child=Svg("assets/power.svg",size=18),
                                      on_clicked=lambda *_: (self.toggle()))
            self.restart = Button(name="power-button",
                                      child=Svg("assets/restart.svg",size=18),
                                      on_clicked=lambda *_: (exec_shell_command_async("reboot") ),visible=False) 
            self.shutdown = Button(name="power-button",
                                      child=Svg("assets/power.svg",size=18),
                                      on_clicked=lambda *_: (exec_shell_command_async("shutdown --now") ),visible=False)
            self.sleep = Button(name="power-button",
                                      child=Svg("assets/sleep.svg",size=18),
                                      on_clicked=lambda *_: (exec_shell_command_async("systemctl suspend") ),visible=False)
            self.active = False

            self.box = Box(visible=True)
            


            self.box.add(self.sleep)
            self.box.add(self.restart)
            self.box.add(self.shutdown)
            
            self.revealer = Revealer(
                child=self.box,
                transition_type="slide-left",
                reveal_child=False,
                name="window-revealer",
                transition_duration=200,)
            
            # self.box_revealer = Box(visible=True, child=self.revealer)

            self.add(self.revealer)
            self.add(self.powerbutton)


            
    def scroll_to_selected(self, button):
        def scroll():
            adj = self.apps.get_vadjustment()
            alloc = button.get_allocation()
            if alloc.height == 0:
                return False  # Retry if allocation isn't ready

            y = alloc.y
            height = alloc.height
            page_size = adj.get_page_size()
            current_value = adj.get_value()

            # Calculate visible boundaries
            visible_top = current_value
            visible_bottom = current_value + page_size

            if y < visible_top:
                # Item above viewport - align to top
                adj.set_value(y)
            elif y + height > visible_bottom:
                # Item below viewport - align to bottom
                new_value = y + height - page_size
                adj.set_value(new_value)
            # No action if already fully visible
            return False
        GLib.idle_add(scroll)


    class LauncherItem(Button):
        def on_button_mouse_click(self, widget, event):
            if event.type == Gdk.EventType.BUTTON_PRESS:
                self.launch()
            return False


        def launch(self):
            self.app.launch()
            self.menu.toggle_visibility()
        def __init__(self, app, menu):
            super().__init__(style_classes="launcher-item")

            self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.connect("button-press-event", self.on_button_mouse_click)

            self.menu = menu
            self.app = app
            self.image = Image(pixbuf=app.get_icon_pixbuf(size=20),)
            self.label = Label(app.display_name, style_classes="launcher-item-label")
            self.box = Box()
            self.box.add(self.image)
            self.box.add(self.label)
            self.add(self.box)
    
    def toggle_menu_button(self):
        if not self.is_active:
            self.toggle_visibility()
        if not self.power_button.active:
            GLib.timeout_add(400, lambda: (self.power_button.toggle(), False)[1])




    def toggle_visibility(self): 
        if self.is_active:
            self.revealer.set_reveal_child(False)
            self.is_active = False
            GLib.timeout_add(self.revealer.transition_duration, lambda: (self.set_visible(False), False)[1])
            if self.power_button.active:
                self.power_button.toggle()

        else:
            self.set_visible(True)
            self.revealer.set_reveal_child(True)
            self.is_active = True
            self._all_apps = get_desktop_applications()

            self.entry.set_text("")
            self.entry.grab_focus()
            self.bake_viewport()
        return False



    def keypressed(self, widget, event):

        match event.keyval:
            case Gdk.KEY_Down:
                self.update_selection(self.selected_index+1)
            case Gdk.KEY_Up:
                self.update_selection(self.selected_index-1)
            case Gdk.KEY_Return:
                self.viewport.get_children()[self.selected_index].launch()
            case Gdk.KEY_KP_Enter: 
                self.viewport.get_children()[self.selected_index].launch()
            # case Gdk.KEY_Escape:
            #     self.viewport.get_children()[self.selected_index].launch()
                # self.toggle_visibility()



            # case Gdk.KEY_Super_L:
            #     self.toggle_visibility()

    def bake_viewport(self, text : str = ""):
            self.filter_apps(text)
            self.viewport.children = []
            self.viewport.children = sorted([self.LauncherItem(app, self) for app in self.filtered_apps],
                                            key=lambda x: x.app.display_name,
                                            reverse=False)
            self.update_selection(0)

    def notify_text(self, entry, *_):
        self.bake_viewport(entry.get_text())

    def update_selection(self, new_index):
        print(self.filtered_apps[new_index].display_name)
        if self.selected_index != -1 and self.selected_index < len(self.viewport.get_children()):
            current_button = self.viewport.get_children()[self.selected_index]
            current_button.get_style_context().remove_class("selected")
            self.scroll_to_selected(current_button)
        if new_index != -1 and new_index < len(self.viewport.get_children()):
            new_button = self.viewport.get_children()[new_index]
            new_button.get_style_context().add_class("selected")
            self.scroll_to_selected(new_button)
            self.selected_index = new_index
        else:
            self.selected_index = -1


    def filter_apps(self, text):
        self.filtered_apps = [obj for obj in self._all_apps if text.lower() in obj.display_name.lower()]

    def __init__(self,):
        super().__init__(
            name="power-menu",
            exclusivity="normal",
            pass_through=False,
            layer="top",
            keyboard_mode="on-demand",
            anchor="top left",
            # visible=False, #False
            # all_visible=False, #False
            margin="1px 0px 0px 0px",
            on_key_press_event=self.keypressed
        )

        self.steal_input()

        self.is_active=False

        self._all_apps = get_desktop_applications()

        self.filtered_apps = self._all_apps

        self.selected_index = 2

        self.illustration = Svg("assets/evangelion.svg",size=200)

        self.viewport = Box(orientation="v",
                            children=[],
                            )

        self.entry = Entry(
                        name="search-entry",
                        placeholder="Search Applications...",
                        h_expand=True,
                        on_activate=lambda entry, *_: self.bake_viewport(entry.get_text()),
                        notify_text=self.notify_text,
                    )

        self.update_selection(2)



        self.apps = ScrolledWindow(
            name="scrolled-window",
            spacing=0,
            min_content_size=(450, 400),
            max_content_size=(450, 400),
            child=self.viewport,)

        self.applauncher = Box(
            name="applauncher",
            children=[
                self.entry,
                self.apps,
            ],
            h_expand=True,
            orientation="v",
        )

        # self.children = Box(children = [
        #     Box(name="test",children=self.applauncher),
        #     CenterBox(style="margin:0.5em;",
        #         start_children=Box(children=self.illustration),
        #         center_children=Box(),
        #         end_children=Box(children=self.PowerButton()),
        #     )
        #
        #     ],
        #     orientation="v",
        #     style="padding:0.5em;")
        self.power_button = self.PowerButton()
        
        self.inner_box = Box(children=[
            Box(name="test", children=[self.applauncher]),
            CenterBox(
                style="margin:0.5em;",
                start_children=Box(children=self.illustration),
                center_children=Box(),
                end_children=Box(children=self.power_button),
            )
        ],
        orientation="v",
        style="padding:0.5em;"
        )

        self.revealer = Revealer(
            child=self.inner_box,
            transition_type="slide-down",
            reveal_child=False,
            name="window-revealer",
            transition_duration=400,
        )
        

        self.add(self.revealer)

        def map_once():
            self.show_all()
            self.hide()
            return False

        GLib.idle_add(map_once)

        def preload():
            self.bake_viewport()
            self.viewport.queue_draw()
            return False

        GLib.idle_add(preload)


        # self.show_all()







