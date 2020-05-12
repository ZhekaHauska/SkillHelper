from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.togglebutton import ToggleButton


class SkillControlPanel(AnchorLayout):
    pass


class SkillControlGroupPanel(AnchorLayout):
    pass


class TaskControlPanel(AnchorLayout):
    pass


class HiddenTogButton(ToggleButton):
    def on_press(self):
        group = self.root.screen_manager.skills_screen.group
        if self.state == 'down':
            self.root.screen_manager.skills_screen.refresh(group=group, hidden=True)
        else:
            self.root.screen_manager.skills_screen.refresh(group=group)
