from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen
from datetime import datetime


class AddTaskScreen(Screen):
    def __init__(self, **kwargs):
        super(AddTaskScreen, self).__init__(**kwargs)
        self.parent_group = None
        self.parent_name = None

    def back(self):
        if len(self.parent_group.split('/')) > 1:
            screen_name = "task_info_screen"
        else:
            screen_name = "skill_info_screen"

        self.manager.current = screen_name
        self.manager.current_screen.item = self.manager.database.find_item(self.parent_group, self.parent_name)


class ApplyTaskInfoButton(Button):
    def add_task(self):
        group = "/".join([self.screen_manager.add_task_screen.parent_group,
                          self.screen_manager.add_task_screen.parent_name])

        check_fails = False

        name = self.task_name.text.strip()
        if name == '':
            check_fails = True
            self.task_name.text = ''
            self.task_name.warning_blink()

        description = self.task_description.text.strip()
        if description == '':
            check_fails = True
            self.task_description.text = ''
            self.task_description.warning_blink()

        try:
            time = float(self.task_time.text)
        except ValueError:
            check_fails = True
            self.task_time.text = ''
            self.task_time.warning_blink()

        try:
            exp_time = float(self.expected_time.text)
        except ValueError:
            check_fails = True
            self.expected_time.text = ''
            self.expected_time.warning_blink()

        deadline = self.deadline.text
        try:
            datetime.strptime(deadline, '%Y-%m-%d %H')
        except ValueError:
            check_fails = True
            self.deadline.warning_blink()
            self.deadline.text = "date in format: YYYY-MM-DD hh(24-hour)"

        if not check_fails:
            task_data = {"name": name,
                         "description": description,
                         "time": time,
                         "deadline": deadline,
                         "expected_time": exp_time,
                         "group": group,
                         "started": datetime.today().strftime("%Y-%m-%d %H")}

            self.screen_manager.database.add_item(task_data)
            self.screen_manager.add_task_screen.back()

