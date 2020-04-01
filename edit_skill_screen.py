from kivy.uix.button import Button


class SaveSkillButton(Button):
    def edit_item(self):
        skill_data = {"name": self.item_name.text,
                      "description": self.item_description.text,
                      "time": float(self.item_time.text),
                      "importance": float(self.item_importance),
                      "group": self.item_group}

        self.screen_manager.db_skills.edit_item(skill_data, self.edit_screen.curr_item['item_id'])
        self.screen_manager.current = 'skills_screen'