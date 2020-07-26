from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from source.database import Database
from kivy.uix.screenmanager import NoTransition

Builder.load_file("source/widgets.kv")
Builder.load_file("source/screen_manager.kv")
Builder.load_file("source/control_panel.kv")
Builder.load_file("source/group_screen.kv")

Builder.load_file("source/skills_screen.kv")
Builder.load_file("source/skills_view.kv")
Builder.load_file("source/skill_info_screen.kv")
Builder.load_file("source/skill_add_screen.kv")
Builder.load_file("source/skill_edit_screen.kv")

Builder.load_file("source/tasks_screen.kv")
Builder.load_file("source/tasks_view.kv")
Builder.load_file("source/task_info_screen.kv")
Builder.load_file("source/task_add_screen.kv")
Builder.load_file("source/task_edit_screen.kv")

Builder.load_file("source/node_editor_screen.kv")


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
