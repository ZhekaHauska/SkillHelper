from kivy.uix.button import Button


class AddTaskButton(Button):
    def add_task(self):
        task_data = {"name": self.task_name.text,
                      "description": self.task_description.text,
                      "time": float(self.task_time.text),
                      "importance:": float(self.task_importance)}

        self.screen_manager.db_tasks.add_item(task_data)
        self.screen_manager.current = 'tasks_screen'

