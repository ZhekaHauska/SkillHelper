from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from database import Database
from kivy.uix.screenmanager import NoTransition

Builder.load_file("skill_helper_widgets.kv")
Builder.load_file("skill_helper_screen_manager.kv")
Builder.load_file("control_panel.kv")
Builder.load_file("group_screen.kv")

Builder.load_file("skills_screen.kv")
Builder.load_file("skills_view.kv")
Builder.load_file("skill_info_screen.kv")
Builder.load_file("add_skill_screen.kv")
Builder.load_file("edit_skill_screen.kv")

Builder.load_file("tasks_screen.kv")
Builder.load_file("tasks_view.kv")
Builder.load_file("task_info_screen.kv")
Builder.load_file("add_task_screen.kv")
Builder.load_file("edit_task_screen.kv")

Builder.load_file("node_editor_screen.kv")


class SkillHelperScreenManager(ScreenManager):
    def __init__(self, database, **kwargs):
        self.database = database
        super(SkillHelperScreenManager, self).__init__(**kwargs)


class SkillHelperApp(App):
    def build(self):
        # link database and interface
        db = Database("hauska")
        db.refresh_groups()
        db.refresh_stats()
        sm = SkillHelperScreenManager(db, transition=NoTransition())

        sm.current = "group_screen"
        return sm


if __name__ == '__main__':
    SkillHelperApp().run()
