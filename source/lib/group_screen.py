from kivy.uix.screenmanager import Screen
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Line, Rectangle, Color
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout


class GroupScreen(Screen):
    group_view = ObjectProperty()

    def __init__(self, **kwargs):
        super(GroupScreen, self).__init__(**kwargs)

    def on_enter(self, *args):
        super(GroupScreen, self).on_enter(*args)
        if (self.group_view is not None) and (self.schedule_info is not None):
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
        self.schedule_info.refresh(self.manager, self.manager.database.data['tasks']['items'])


class GroupButton(Button):
    def __init__(self, group, screen_manager, **kwargs):
        super(GroupButton, self).__init__(**kwargs)
        self.group = group['name']
        self.screen_manager = screen_manager
        self.orientation = 'vertical'
        self.size_hint_x = None
        self.width = 150
        self.markup = True
        text = [f"[size=18][b]{group['name']}[/b][/size]",
                f"[size=12]Priority: {round(group['priority'], 2)}[/size]",
                f"[size=12]Speed: {round(group['speed'], 2)} ({round(group['expected_speed'], 2)}) h/d[/size]"]

        self.text = text[0] + '\n' + text[1] + '\n' + text[2]

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
        self.box_layout.clear_widgets()

        for group in groups:
            button = GroupButton(group=group, screen_manager=manager)
            self.box_layout.add_widget(button)


class TasksItemInfo(Label):
    def __init__(self, manager, task, **kwargs):
        super(TasksItemInfo, self).__init__(**kwargs)
        self.manager = manager
        self.task = task
        self.selected = None
        self.halign = 'left'
        self.markup = True
        self.text = f"[u]{task['group'] +'/'+ task['name']}[/u] | [b]{task['deadline']}[/b] | {round(task['remain'], 2)}"

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            with self.canvas:
                Color(1, 1, 1)
                x, y = self.to_parent(0, 0, relative=True)
                self.selected = Line(rectangle=(x, y, self.width, self.height), dash_offset=2)
            return True
        return super(TasksItemInfo, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.selected:
            self.canvas.remove(self.selected)
            self.selected = None
            sm = self.manager

            sm.task_info_screen.item = self.task
            sm.current = 'task_info_screen'

            return True
        return super(TasksItemInfo, self).on_touch_up(touch)


class ScheduleInfo(RelativeLayout):
    def __init__(self, **kwargs):
        super(ScheduleInfo, self).__init__(**kwargs)
        self.box_layout = BoxLayout(orientation='vertical')
        self.add_widget(self.box_layout)

    def refresh(self, manager, tasks):
        self.box_layout.clear_widgets()

        self.box_layout.add_widget(Label(text="[size=20][b][color=ff3333]Closest deadlines:[/color][/b][/size]",
                                         size_hint=(1, 1), markup=True, valign='middle'))
        sorted_tasks = sorted(tasks, key=lambda x: x['remain'])[:3]
        for item in sorted_tasks:
            label = TasksItemInfo(manager, item)
            self.box_layout.add_widget(label)






