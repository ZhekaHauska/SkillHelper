from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class AddSkillScreen(Screen):
    def __init__(self, **kwargs):
        super(AddSkillScreen, self).__init__(**kwargs)


class AddSkillButton(Button):
    def add_skill(self):
        skill_data = {"name": self.skill_name.text,
                      "description": self.skill_description.text,
                      "time": float(self.skill_time.text),
                      "group": self.skill_group,
                      "importance": 0}

        self.screen_manager.database.add_item(skill_data)
        self.screen_manager.skills_screen.group = skill_data['group']
        self.screen_manager.current = 'skills_screen'
