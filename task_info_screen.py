from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


class AttrDict(object):
    def __init__(self, dict):
        self.__dict__ = dict


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
            
    def refresh(self, item):
        self.item_name.text = item.name
        self.item_description.text = item.description
        self.item_time.text = str(round(item.time, 2))
        self.item_group.text = item.group

        items = self.manager.database.get_items("tasks", item.group + "/" + item.name)
        self.items_view.data = items
        self.items_view.refresh_from_data()


class AddTaskTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.skill_info_screen.item_group.text,
                                              self.skill_info_screen.item_name.text,
                                              float(self.add_time_amount.text))
        new_time = float(self.task_info_screen.item_time.text) + float(self.add_time_amount.text)
        self.task_info_screen.item_time.text = str(round(new_time, 2))


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


class TaskBackButton(Button):
    def on_press(self):
        self.screen_manager.current = "skill_info_screen"
        skill_name = self.screen_manager.task_info_screen.item_group.text.split("/")
        skill = self.screen_manager.database.find_item(skill_name[0], skill_name[1])
        skill = AttrDict(skill)
        self.screen_manager.skill_info_screen.refresh(skill)