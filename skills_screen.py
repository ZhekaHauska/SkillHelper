from kivy.uix.screenmanager import Screen


class SkillsScreen(Screen):
    def refresh(self, group=None):
        if group is None:
            items = self.manager.database.skills
            stats = self.manager.database.stats['total']
        else:
            items = self.manager.database.get_items("skills", group)
            try:
                stats = self.manager.database.stats[group]
            except KeyError:
                self.manager.database.refresh_stats(group)
                stats = self.manager.database.stats[group]

        self.items_view.data = items
        self.items_view.refresh_from_data()
        self.stats.text = f"Today: {round(stats['today'], 2)} This week: {round(stats['week'], 2)}"