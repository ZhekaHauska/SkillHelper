from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from source.lib.database import Database
from kivy.uix.screenmanager import NoTransition

from source.lib.timeline_screen import *
from source.lib.widgets import *
from source.lib.task_info_screen import *
from source.lib.skill_info_screen import *
from source.lib.control_panel import *
from source.lib.group_screen import *
from source.lib.node_editor_screen import *
from source.lib.skill_add_screen import *
from source.lib.skills_screen import *
from source.lib.skills_view import *
from source.lib.task_add_screen import *
from source.lib.tasks_view import *
from source.lib.tasks_screen import *

Builder.load_file("source/kv/widgets.kv")
Builder.load_file("source/kv/control_panel.kv")
Builder.load_file("source/kv/group_screen.kv")

Builder.load_file("source/kv/skills_screen.kv")
Builder.load_file("source/kv/skills_view.kv")
Builder.load_file("source/kv/skill_info_screen.kv")
Builder.load_file("source/kv/skill_add_screen.kv")

Builder.load_file("source/kv/tasks_screen.kv")
Builder.load_file("source/kv/tasks_view.kv")
Builder.load_file("source/kv/task_info_screen.kv")
Builder.load_file("source/kv/task_add_screen.kv")

Builder.load_file("source/kv/node_editor_screen.kv")
Builder.load_file("source/kv/timeline_screen.kv")


class SkillHelperScreenManager(ScreenManager):
    def __init__(self, database, **kwargs):
        super(SkillHelperScreenManager, self).__init__(**kwargs)
        self.database = database

        self.group_screen = GroupScreen()
        self.add_widget(self.group_screen)

        self.skills_screen = SkillsScreen()
        self.add_widget(self.skills_screen)

        self.skill_info_screen = SkillInfoScreen()
        self.add_widget(self.skill_info_screen)

        self.add_skill_screen = AddSkillScreen()
        self.add_widget(self.add_skill_screen)

        self.tasks_screen = TasksScreen()
        self.add_widget(self.tasks_screen)

        self.task_info_screen = TaskInfoScreen()
        self.add_widget(self.task_info_screen)

        self.add_task_screen = AddTaskScreen()
        self.add_widget(self.add_task_screen)

        self.node_editor_screen = NodeEditorScreen()
        self.add_widget(self.node_editor_screen)

        self.timeline_screen = TimelineScreen()
        self.add_widget(self.timeline_screen)


class SkillHelperApp(App):
    def build(self):
        # link database and interface
        db = Database("hauska")
        sm = SkillHelperScreenManager(db, transition=NoTransition())

        sm.current = "group_screen"
        return sm


if __name__ == '__main__':
    SkillHelperApp().run()
