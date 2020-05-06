from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


class TaskInfoScreen(Screen):
    def __init__(self, **kw):
        super(TaskInfoScreen, self).__init__(**kw)

    def toggle_view(self):
        if self.manager.database.show_hidden:
            self.options.disabled = True
            self.unhide_button.disabled = False
        else:
            self.options.disabled = False
            self.unhide_button.disabled = True


class AddTaskTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.task_info_screen.curr_item['item_id'],
                                              float(self.add_time_amount.text))


class RemoveTaskButton(Button):
    def remove_task(self):
        self.screen_manager.db_tasks.remove_item(self.task_info_screen.curr_item['item_id'])
        self.screen_manager.current = "tasks_screen"


class HideTaskButton(Button):
    def hide_task(self):
        self.screen_manager.db_tasks.hide_item(self.task_info_screen.curr_item['item_id'])
        self.screen_manager.current = "tasks_screen"


class UnhideTaskButton(Button):
    def unhide_task(self):
        self.screen_manager.db_tasks.unhide_item(self.task_info_screen.curr_item['item_id'])
        self.screen_manager.current = "tasks_screen"


class EditTaskButton(Button):
    def edit_item(self):
        self.screen_manager.current = "edit_task_screen"
        self.screen_manager.db_tasks.refresh_edit(self.task_info_screen.curr_item["item_id"])