from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button


class SkillInfoScreen(Screen):
    def __init__(self, **kw):
        super(SkillInfoScreen, self).__init__(**kw)

    def toggle_view(self):
        if self.manager.db_skills.show_hidden:
            self.options.disabled = True
            self.unhide_button.disabled = False
        else:
            self.options.disabled = False
            self.unhide_button.disabled = True


class AddTimeButton(Button):
    def add_time(self):
        self.screen_manager.db_skills.add_time(self.skill_info_screen.curr_item["item_id"],
                                              float(self.add_time_amount.text))


class RemoveSkillButton(Button):
    def remove_skill(self):
        self.screen_manager.db_skills.remove_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class HideSkillButton(Button):
    def hide_skill(self):
        self.screen_manager.db_skills.hide_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class UnhideSkillButton(Button):
    def unhide_skill(self):
        self.screen_manager.db_skills.unhide_item(self.skill_info_screen.curr_item["item_id"])
        self.screen_manager.current = "skills_screen"


class EditSkillButton(Button):
    def edit_item(self):
        self.screen_manager.current = "edit_skill_screen"
        self.screen_manager.db_skills.refresh_edit(self.skill_info_screen.curr_item["item_id"])
