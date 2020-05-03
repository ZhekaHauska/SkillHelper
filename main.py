from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from database import Database

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
    def __init__(self, db_skills, db_tasks, **kwargs):
        self.db_skills = db_skills
        self.db_tasks = db_tasks
        super(SkillHelperScreenManager, self).__init__(**kwargs)


class SkillHelperApp(App):
    def build(self):
        # link database and interface
        db_skills = Database("skills")
        db_tasks = Database("tasks")
        sm = SkillHelperScreenManager(db_skills=db_skills, db_tasks=db_tasks)

        db_skills.view_screen = sm.skills_screen
        db_skills.info_screen = sm.skill_info_screen
        db_skills.edit_screen = sm.edit_skill_screen
        db_skills.group_screen = sm.group_screen

        db_tasks.view_screen = sm.tasks_screen
        db_tasks.info_screen = sm.task_info_screen
        db_tasks.edit_screen = sm.edit_task_screen
        # initialize view
        db_skills.refresh_stats()
        db_tasks.refresh_stats()

        sm.current = "group_screen"
        return sm


if __name__ == '__main__':
    SkillHelperApp().run()
