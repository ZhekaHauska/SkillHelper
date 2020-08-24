from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen


class AddSkillScreen(Screen):
    def __init__(self, **kwargs):
        super(AddSkillScreen, self).__init__(**kwargs)


class ApplySkillInfoButton(Button):
    def add_skill(self):
        check_fails = False

        name = self.skill_name.text.strip()
        if name == '':
            check_fails = True
            self.skill_name.text = ''
            self.skill_name.warning_blink()

        description = self.skill_description.text.strip()
        if description == '':
            check_fails = True
            self.skill_description.text = ''
            self.skill_description.warning_blink()

        group = self.skill_group.text.strip()
        if group == '':
            check_fails = True
            self.skill_group.text = ''
            self.skill_group.warning_blink()

        try:
            time = float(self.skill_time.text)
        except ValueError:
            check_fails = True
            self.skill_time.text = ''
            self.skill_time.warning_blink()

        importance = 0

        if not check_fails:
            skill_data = {"name": name,
                          "description": description,
                          "time": time,
                          "group": group,
                          "importance": importance}

            self.screen_manager.database.add_item(skill_data)
            self.screen_manager.skills_screen.group = skill_data['group']
            self.screen_manager.current = 'skills_screen'
