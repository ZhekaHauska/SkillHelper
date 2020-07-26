from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class TaskInfoScreen(Screen):
    item = ObjectProperty(allownone=True)

    def __init__(self, **kw):
        super(TaskInfoScreen, self).__init__(**kw)

    def on_item(self, *args):
        if self.item is not None:
            self.refresh()

    def refresh(self):
        if self.item['hidden']:
            self.options.disabled = True
            self.unhide_button.disabled = False
            self.hide_button.disabled = True
        else:
            self.options.disabled = False
            self.unhide_button.disabled = True
            self.hide_button.disabled = False

        self.item_name.text = self.item['name']
        self.item_description.text = self.item['description']
        self.item_time.text = str(round(self.item['time'], 2))
        self.item_group.text = self.item['group']
        self.deadline.text = f"Deadline: {self.item['deadline']}"
        self.expected_time.text = f"Expected time: {round(self.item['expected_time'], 2)} hours"
        self.remains.text = f"Remain: {round(self.item['remain'], 2)} hours"

        self.refresh_tasks(self.item['group'] + "/" + self.item['name'])

        self.manager.add_task_screen.parent_group = self.item['group']
        self.manager.add_task_screen.parent_name = self.item['name']

    def refresh_tasks(self, group, hidden=False):
        items = self.manager.database.get_items("tasks", group, hidden=hidden)
        self.items_view.data = items
        self.items_view.refresh_from_data()

    def on_pre_enter(self, *args):
        super(TaskInfoScreen, self).on_pre_enter(*args)
        self.control_panel.tog_button.state = 'normal'

    def on_enter(self, *args):
        super(TaskInfoScreen, self).on_enter(*args)
        if self.item is not None:
            self.refresh()

    def on_leave(self, *args):
        super(TaskInfoScreen, self).on_leave(*args)
        if self.item is not None:
            self.save()
    
    def back(self):
        item_name = self.item_group.text.split("/")
        item = self.manager.database.find_item("/".join(item_name[:-1]), item_name[-1])

        if len(item_name) > 2:
            screen_name = "task_info_screen"
        else:
            screen_name = "skill_info_screen"

        self.manager.current = screen_name
        self.manager.get_screen(screen_name).item = item

    def save(self):
        self.manager.database.edit_item(self.item['group'], self.item['name'],
                                        {'description': self.item_description.text}, self.item['hidden'])


class AddTaskTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.screen_manager.task_info_screen.item['group'],
                                              self.screen_manager.task_info_screen.item['name'],
                                              float(self.add_time_amount.text))
        new_time = float(self.screen_manager.task_info_screen.item_time.text) + float(self.add_time_amount.text)
        self.screen_manager.task_info_screen.item_time.text = str(round(new_time, 2))


class RemoveTaskButton(Button):
    def remove_task(self):
        self.screen_manager.database.remove_item(self.task_info_screen.item_group.text,
                                                 self.task_info_screen.item_name.text,
                                                 hidden=self.task_info_screen.item['hidden'])
        self.screen_manager.task_info_screen.item = None
        self.screen_manager.task_info_screen.back()


class HideTaskButton(Button):
    def hide_task(self):
        item = self.screen_manager.database.hide_item(self.task_info_screen.item_group.text,
                                                      self.task_info_screen.item_name.text)
        self.screen_manager.task_info_screen.item = item
        self.screen_manager.task_info_screen.refresh()


class UnhideTaskButton(Button):
    def unhide_task(self):
        item = self.screen_manager.database.unhide_item(self.task_info_screen.item_group.text,
                                                        self.task_info_screen.item_name.text)
        self.screen_manager.task_info_screen.item = item
        self.screen_manager.task_info_screen.refresh()


class TaskBackButton(Button):
    def on_press(self):
        self.screen_manager.task_info_screen.save()
        self.screen_manager.task_info_screen.back()

