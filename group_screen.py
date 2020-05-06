from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class GroupScreen(Screen):
    pass


class GroupButton(Button):
    def __init__(self, group, screen_manager, **kwargs):
        super(GroupButton, self).__init__(**kwargs)
        self.group = group
        self.screen_manager = screen_manager
        self.text = group
        self.text_size = self.size

    def on_press(self):
        self.screen_manager.current = "skills_screen"
        self.screen_manager.database.current_group = self.group
        self.screen_manager.database.refresh_stats()
        items = self.screen_manager.database.get_items("skills", self.group)
        self.screen_manager.skills_screen.items_view.data = items
        self.screen_manager.skills_screen.items_view.refresh_from_data()


class GroupView(BoxLayout):
    groups = ObjectProperty()

    def __init__(self, **kwargs):
        super(GroupView, self).__init__(**kwargs)
        self.buttons = list()

    def on_groups(self, instance, value):
        for button in self.buttons:
            self.remove_widget(button)
        self.buttons = list()
        for group in self.groups:
            button = GroupButton(group=group, screen_manager=self.screen_manager)
            self.buttons.append(button)
            self.add_widget(button)
