from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import BooleanProperty


class SkillInfoScreen(Screen):
    def __init__(self, **kw):
        super(SkillInfoScreen, self).__init__(**kw)
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
        super(SkillInfoScreen, self).on_enter(*args)
        self.refresh(self.item, hidden=self.manager.skills_screen.hidden)


class AddTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.skill_info_screen.item_group.text,
                                              self.skill_info_screen.item_name.text,
                                              float(self.add_time_amount.text))
        new_time = float(self.skill_info_screen.item_time.text) + float(self.add_time_amount.text)
        self.skill_info_screen.item_time.text = str(round(new_time, 2))


class RemoveSkillButton(Button):
    def remove_skill(self):
        self.screen_manager.database.remove_item(self.skill_info_screen.item_group.text,
                                                 self.skill_info_screen.item_name.text,
                                                 hidden=self.screen_manager.skills_screen.hidden)
        self.screen_manager.current = "skills_screen"


class HideSkillButton(Button):
    def hide_skill(self):
        self.screen_manager.database.hide_item(self.skill_info_screen.item_group.text,
                                               self.skill_info_screen.item_name.text)
        self.screen_manager.current = "skills_screen"


class UnhideSkillButton(Button):
    def unhide_skill(self):
        self.screen_manager.database.unhide_item(self.skill_info_screen.item_group.text,
                                                 self.skill_info_screen.item_name.text)
        self.screen_manager.current = "skills_screen"


class EditSkillButton(Button):
    def edit_item(self):
        self.screen_manager.current = "edit_skill_screen"
