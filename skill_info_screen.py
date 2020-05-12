from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


class SkillInfoScreen(Screen):
    def __init__(self, **kw):
        super(SkillInfoScreen, self).__init__(**kw)

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


class AddTimeButton(Button):
    def add_time(self):
        self.screen_manager.database.add_time(self.skill_info_screen.item_group.text,
                                              self.skill_info_screen.item_name.text,
                                              float(self.add_time_amount.text))
        new_time = float(self.skill_info_screen.item_time.text) + float(self.add_time_amount.text)
        self.skill_info_screen.item_time.text = str(round(new_time, 2))


class RemoveSkillButton(Button):
    def remove_skill(self):
        self.screen_manager.database.remove_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class HideSkillButton(Button):
    def hide_skill(self):
        self.screen_manager.database.hide_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class UnhideSkillButton(Button):
    def unhide_skill(self):
        self.screen_manager.database.unhide_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class EditSkillButton(Button):
    def edit_item(self):
        self.screen_manager.current = "edit_skill_screen"
