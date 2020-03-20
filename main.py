from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from database import Database

Builder.load_file("skill_helper_widgets.kv")
Builder.load_file("skill_helper_screen_manager.kv")
Builder.load_file("control_panel.kv")

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
    pass


class SkillHelperApp(App):
    def build(self):
        # link database and interface
        sm = SkillHelperScreenManager()
        db_skills = Database("skills", sm.skills_screen, sm.skill_info_screen, sm.edit_skill_screen)
        db_tasks = Database("tasks", sm.tasks_screen, sm.task_info_screen, sm.edit_task_screen)
        sm.db_skills = db_skills
        sm.db_tasks = db_tasks
        # initialize view
        db_skills.refresh_view()
        db_skills.refresh_stats()
        db_tasks.refresh_view()
        db_tasks.refresh_stats()

        sm.current = "skills_screen"
        return sm


if __name__ == '__main__':
    SkillHelperApp().run()
