from kivy.uix.button import Button


class AddSkillButton(Button):
    def add_skill(self):
        skill_data = {"name": self.skill_name.text,
                      "description": self.skill_description.text,
                      "time": float(self.skill_time.text),
                      "importance": float(self.skill_importance),
                      "group": self.skill_group}

        self.screen_manager.db_skills.add_item(skill_data)
        self.screen_manager.current = 'skills_screen'
