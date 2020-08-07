from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Line, Rectangle


class GroupScreen(Screen):
    group_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(GroupScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        super(GroupScreen, self).on_enter(*args)
        if self.group_view is not None:
            self.refresh()

    def refresh(self, *args):
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

        self.group_view.refresh(self.manager, self.manager.database.data['groups'])


class GroupButton(Button):
    def __init__(self, group, screen_manager, **kwargs):
        super(GroupButton, self).__init__(**kwargs)
        self.group = group['name']
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = 150
        text = [f"{group['name']}", f"Priority: {round(group['priority'], 2)}",
                f"Speed: {round(group['speed'], 2)} ({round(group['expected_speed'], 2)}) h/d"]

        self.text = text[0] + '\n' + text[1] + '\n' + text[2]
        # self.button = Button(text=group['name'])
        # self.button.bind(on_press=self.on_press)
        # self.button.text_size = self.button.size
        # self.button.halign = 'center'
        # self.button.valign = 'center'
        #
        # self.add_widget(self.button)
        #
        # self.label = Label(text=text[0] + '\n' + text[1])
        #
        # self.add_widget(self.label)

    def on_press(self, *args):
        self.screen_manager.current = "skills_screen"
        self.screen_manager.skills_screen.refresh(self.group)


class GroupView(ScrollView):
    def __init__(self, **kwargs):
        super(GroupView, self).__init__(**kwargs)
        self.box_layout = BoxLayout(orientation='horizontal', size_hint_x=None,
                                    spacing=2, padding=[1, 1, 1, 1])
        self.box_layout.bind(minimum_width=self.box_layout.setter('width'))
        self.add_widget(self.box_layout)

    def refresh(self, manager, groups):
        # self.manager = manager
        self.box_layout.clear_widgets()

        for group in groups:
            button = GroupButton(group=group, screen_manager=manager)
            # button = Button(text=group['name'], size_hint_x=None, width=100)
            # button.bind(on_press=self.back)
            self.box_layout.add_widget(button)

    def back(self, *args):
        self.manager.current = 'skills_screen'

