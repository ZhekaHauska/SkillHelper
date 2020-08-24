from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from functools import partial


class SkillInfoScreen(Screen):
    item = ObjectProperty(allownone=True)

    def __init__(self, **kwargs):
        super(SkillInfoScreen, self).__init__(**kwargs)

    def on_item(self, *args):
        if self.item is not None:
            self.refresh()

    def refresh(self, *args):
        if self.item['hidden']:
            self.hide_button.background_normal = 'source/res/unhide.png'
            self.hide_button.background_down = 'source/res/unhide_active.png'
            self.timer.disabled = True
            self.add_time.disabled = True
            self.control_panel.disabled = True
            self.items_view.disabled = True
        else:
            self.hide_button.background_normal = 'source/res/hide.png'
            self.hide_button.background_down = 'source/res/hide_active.png'
            self.timer.disabled = False
            self.add_time.disabled = False
            self.control_panel.disabled = False
            self.items_view.disabled = False

        self.item_name.text = self.item['name']
        self.item_description.text = self.item['description']
        self.item_time.text = str(round(self.item['time'], 2))
        self.item_group.text = self.item['group']
        # stats
        stats = self.manager.database.refresh_stats(self.item['group'], self.item['name'])
        self.stats.text = f"""Total time for two weeks: {round(self.item['time2w'], 2)}    This week: {round(stats['week'], 2)}    Today: {round(stats['today'], 2)}"""

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

    def save(self, data):
        self.manager.database.edit_item(self.item['group'], self.item['name'],
                                        data,
                                        self.item['hidden'])


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
            self.screen_manager.group_screen.refresh()

            self.screen_manager.skill_info_screen.item_time.text += f" + {round(dt, 2)}"
            self.add_time_amount.text = '0'
            Clock.schedule_once(self.screen_manager.skill_info_screen.refresh, 3)

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
        if self.skill_info_screen.item['hidden']:
            item = self.screen_manager.database.unhide_item(self.skill_info_screen.item_group.text,
                                                            self.skill_info_screen.item_name.text)
            self.screen_manager.skill_info_screen.item = item
            self.screen_manager.skill_info_screen.refresh()
        else:
            item = self.screen_manager.database.hide_item(self.skill_info_screen.item_group.text,
                                                          self.skill_info_screen.item_name.text)
            self.screen_manager.skill_info_screen.item = item
            self.screen_manager.skill_info_screen.refresh()



