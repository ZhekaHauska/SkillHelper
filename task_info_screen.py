from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


class AttrDict(object):
    def __init__(self, dict):
        self.__dict__ = dict


class TaskInfoScreen(Screen):
    def __init__(self, **kw):
        super(TaskInfoScreen, self).__init__(**kw)
        self.item = None

    def refresh(self, item, hidden=False):
        self.item = item
        if hidden:
            self.options.disabled = True
            self.unhide_button.disabled = False
            self.hide_button.disabled = True
        else:
            self.options.disabled = False
            self.unhide_button.disabled = True
            self.hide_button.disabled = False

        self.item_name.text = item.name
        self.item_description.text = item.description
        self.item_time.text = str(round(item.time, 2))
        self.item_group.text = item.group

        self.refresh_tasks(item.group + "/" + item.name)

        self.manager.add_task_screen.parent_group = item.group
        self.manager.add_task_screen.parent_name = item.name

    def refresh_tasks(self, group, hidden=False):
        items = self.manager.database.get_items("tasks", group, hidden=hidden)
        self.items_view.data = items
        self.items_view.refresh_from_data()

    def on_enter(self, *args):
        super(TaskInfoScreen, self).on_enter(*args)
        self.refresh(self.item, hidden=self.manager.skills_screen.hidden)


class AddTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.task_info_screen.item_group.text,
                                              self.task_info_screen.item_name.text,
                                              float(self.add_time_amount.text))
        new_time = float(self.task_info_screen.item_time.text) + float(self.add_time_amount.text)
        self.task_info_screen.item_time.text = str(round(new_time, 2))


class RemoveTaskButton(Button):
    def remove_task(self):
        self.screen_manager.database.remove_item(self.task_info_screen.item_group.text,
                                                 self.task_info_screen.item_name.text,
                                                 hidden=self.screen_manager.tasks_screen.hidden)
        self.screen_manager.current = "skills_screen"


class HideTaskButton(Button):
    def hide_task(self):
        self.screen_manager.database.hide_item(self.task_info_screen.item_group.text,
                                               self.task_info_screen.item_name.text)
        self.screen_manager.current = "skills_screen"


class UnhideTaskButton(Button):
    def unhide_task(self):
        self.screen_manager.database.unhide_item(self.task_info_screen.item_group.text,
                                                 self.task_info_screen.item_name.text)
        self.screen_manager.current = "skills_screen"


class EditTaskButton(Button):
    def edit_item(self):
        self.screen_manager.current = "edit_skill_screen"


class TaskBackButton(Button):
    def on_press(self):
        self.screen_manager.current = "skill_info_screen"
        skill_name = self.screen_manager.task_info_screen.item_group.text.split("/")
        skill = self.screen_manager.database.find_item(skill_name[0], skill_name[1])
        skill = AttrDict(skill)
        self.screen_manager.skill_info_screen.refresh(skill)