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

Builder.load_file("source/kv/widgets.kv")
Builder.load_file("source/kv/screen_manager.kv")
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
        self.database = database
        super(SkillHelperScreenManager, self).__init__(**kwargs)


class SkillHelperApp(App):
    def build(self):
        # link database and interface
        db = Database("hauska")
        sm = SkillHelperScreenManager(db, transition=NoTransition())

        sm.current = "group_screen"
        return sm


if __name__ == '__main__':
    SkillHelperApp().run()
