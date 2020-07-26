from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class AddTaskScreen(Screen):
    def __init__(self, **kwargs):
        super(AddTaskScreen, self).__init__(**kwargs)
        self.parent_group = None
        self.parent_name = None

    def back(self):
        if len(self.parent_group.split('/')) > 2:
            screen_name = "task_info_screen"
        else:
            screen_name = "skill_info_screen"

        self.manager.current = screen_name


class AddTaskButton(Button):
    def add_task(self):
        group = "/".join([self.screen_manager.add_task_screen.parent_group,
                          self.screen_manager.add_task_screen.parent_name])
        task_data = {"name": self.task_name.text,
                     "description": self.task_description.text,
                     "time": float(self.task_time.text),
                     "deadline": self.deadline.text,
                     "expected_time": float(self.expected_time.text),
                     "group": group}

        self.screen_manager.database.add_item(task_data)
        if len(self.screen_manager.add_task_screen.parent_group.split('/')) > 2:
            screen_name = "task_info_screen"
        else:
            screen_name = "skill_info_screen"

        self.screen_manager.current = screen_name

        self.screen_manager.add_task_screen.back()

