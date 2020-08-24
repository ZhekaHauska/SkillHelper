from kivy.uix.screenmanager import Screen


class SkillsScreen(Screen):
    def __init__(self, **kwargs):
        super(SkillsScreen, self).__init__(**kwargs)
        self.group = None
        self.hidden = False

    def on_pre_enter(self, *args):
        super(SkillsScreen, self).on_pre_enter(*args)
        self.control_panel.tog_button.state = 'normal'
        self.refresh(self.group, self.hidden)

    def refresh(self, group=None, hidden=False):
        self.group = group
        if group is not None:
            self.group_name = group

        self.hidden = hidden
        if hidden:
            if group is None:
                items = self.manager.database.data['skills']['hidden']
            else:
                items = self.manager.database.get_items("skills", group, hidden=True)
        else:
            if group is None:
                items = self.manager.database.data['skills']['items']
                self.manager.database.refresh_stats()
                stats = self.manager.database.stats['total']
            else:
                items = self.manager.database.get_items("skills", group)
                self.manager.database.refresh_stats(group)
                stats = self.manager.database.stats[group]
            self.stats.text = f"Today: {round(stats['today'], 2)} This week: {round(stats['week'], 2)}"

        self.items_view.data = items
        self.items_view.refresh_from_data()
