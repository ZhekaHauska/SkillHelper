from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label


class GroupScreen(Screen):
    def __init__(self, **kwargs):
        super(GroupScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        super(GroupScreen, self).on_pre_enter(*args)
        try:
            self.group_view.groups = self.manager.database.data['groups']
            self.refresh()
        except AttributeError:
            pass

    def refresh(self):
        self.manager.database.refresh_stats()
        stats = self.manager.database.stats['total']
        total_speed = 0
        for x in self.manager.database.data['groups']:
            total_speed += x['expected_speed']
        self.stats.text = f"Today: {round(stats['today'], 2)} This week: {round(stats['week'], 2)}"
        self.speed.text = f"Expected speed: {round(total_speed, 2)} h/d"
        if total_speed > stats['today'] and total_speed > 8:
            self.speed.color = (1, 0, 0, 1)
        else:
            self.speed.color = (0, 0, 1, 1)

        self.group_view.refresh()


class GroupButton(Button):
    def __init__(self, group, screen_manager, **kwargs):
        super(GroupButton, self).__init__(**kwargs)
        self.group = group['name']
        self.screen_manager = screen_manager
        self.text = group['name']
        self.text_size = self.size

    def on_press(self):
        self.screen_manager.current = "skills_screen"
        self.screen_manager.skills_screen.refresh(self.group)


class GroupView(GridLayout):
    groups = ObjectProperty()

    def __init__(self, **kwargs):
        super(GroupView, self).__init__(**kwargs)
        self.rows = 2
        self.buttons = list()
        self.labels = list()

    def refresh(self):
        for group, label in zip(self.groups, self.labels):
            label.text = f"\nPriority: {round(group['priority'], 2)}\nSpeed: {round(group['speed'], 2)} ({round(group['expected_speed'], 2)}) h/d"

    def on_groups(self, instance, value):
        for button, label in zip(self.buttons, self.labels):
            self.remove_widget(button)
            self.remove_widget(label)
        self.buttons = list()
        self.labels = list()

        cols = len(self.groups)
        self.cols = cols
        for group in self.groups:
            button = GroupButton(group=group, screen_manager=self.screen_manager, valign='center', halign='center')
            self.buttons.append(button)
            self.add_widget(button)

        for group in self.groups:
            text = f"""Priority: {round(group['priority'], 2)}

                       Speed: {round(group['speed'], 2)} ({round(group['expected_speed'], 2)}) h/d"""
            label = Label(text=text, valign='top')
            label.text_size = label.size
            self.labels.append(label)
            self.add_widget(label)

        self.group_screen.refresh()
