from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty


class SkillInfoScreen(Screen):
    item = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super(SkillInfoScreen, self).__init__(**kwargs)

    def on_item(self, *args):
        if self.item is not None:
            self.refresh()

    def refresh(self):
        if self.item['hidden']:
            self.options.disabled = True
            self.unhide_button.disabled = False
            self.hide_button.disabled = True
            self.control_panel.disabled = True
            self.items_view.disabled = True
        else:
            self.options.disabled = False
            self.unhide_button.disabled = True
            self.hide_button.disabled = False
            self.control_panel.disabled = False
            self.items_view.disabled = False

        self.item_name.text = self.item['name']
        self.item_description.text = self.item['description']
        self.item_time.text = str(round(self.item['time'], 2))
        self.item_group.text = self.item['group']

        self.refresh_tasks(self.item['group'] + "/" + self.item['name'], self.item['hidden'])

        self.manager.add_task_screen.parent_group = self.item['group']
        self.manager.add_task_screen.parent_name = self.item['name']

    def refresh_tasks(self, group, hidden=False):
        items = self.manager.database.get_items("tasks", group, hidden=hidden)
        self.items_view.data = items
        self.items_view.refresh_from_data()

    def on_pre_enter(self, *args):
        super(SkillInfoScreen, self).on_pre_enter(*args)
        self.control_panel.tog_button.state = 'normal'

    def on_enter(self, *args):
        super(SkillInfoScreen, self).on_enter(*args)
        if self.item is not None:
            self.refresh()

    def on_leave(self, *args):
        super(SkillInfoScreen, self).on_leave(*args)
        if self.item is not None:
            self.manager.database.edit_item(self.item['group'], self.item['name'],
                                            {'description': self.item_description.text}, self.item['hidden'])


class AddSkillTimeButton(Button):
    def add_time(self):
        success = True
        try:
            dt = float(self.add_time_amount.text)
        except ValueError:
            dt = 0
            success = False

        if success:
            self.screen_manager.database.add_time(self.screen_manager.skill_info_screen.item_group.text,
                                                  self.screen_manager.skill_info_screen.item_name.text,
                                                  dt)
            new_time = float(self.screen_manager.skill_info_screen.item_time.text) + dt
            self.screen_manager.skill_info_screen.item_time.text = str(round(new_time, 2))
        else:
            self.add_time_amount.text = '0'
            self.add_time_amount.warning_blink()


class RemoveSkillButton(Button):
    def remove_skill(self):
        self.screen_manager.database.remove_item(self.skill_info_screen.item_group.text,
                                                 self.skill_info_screen.item_name.text,
                                                 hidden=self.skill_info_screen.item['hidden'])
        self.screen_manager.skill_info_screen.item = None
        self.screen_manager.current = "skills_screen"


class HideSkillButton(Button):
    def hide_skill(self):
        item = self.screen_manager.database.hide_item(self.skill_info_screen.item_group.text,
                                                      self.skill_info_screen.item_name.text)
        self.screen_manager.skill_info_screen.item = item
        self.screen_manager.skill_info_screen.refresh()


class UnhideSkillButton(Button):
    def unhide_skill(self):
        item = self.screen_manager.database.unhide_item(self.skill_info_screen.item_group.text,
                                                        self.skill_info_screen.item_name.text)
        self.screen_manager.skill_info_screen.item = item
        self.screen_manager.skill_info_screen.refresh()


