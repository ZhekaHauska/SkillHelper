from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class AddTaskScreen(Screen):
    def __init__(self, **kwargs):
        super(AddTaskScreen, self).__init__(**kwargs)
        self.parent_group = None
        self.parent_name = None


class AddTaskButton(Button):
    def add_task(self):
        group = "/".join([self.screen_manager.add_task_screen.parent_group,
                          self.screen_manager.add_task_screen.parent_name])
        task_data = {"name": self.task_name.text,
                     "description": self.task_description.text,
                     "time": float(self.task_time.text),
                     "importance:": float(self.task_importance),
                     "group": group}

        self.screen_manager.database.add_item(task_data)
        self.screen_manager.current = 'skill_info_screen'

