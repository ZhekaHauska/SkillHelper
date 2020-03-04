import yaml


class Formats:
    def name_format(self, name):
        return name

    def time_format(self, time):
        return f"Total time: {time} hours"

    def description_format(self, description):
        return description


class Database:
    def __init__(self, db_name, view_screen, info_screen, settings_screen):
        self.db_name = db_name
        self.show_hidden = False
        self.view_screen = view_screen
        self.info_screen = info_screen
        self.settings_screen = settings_screen
        self.formats = Formats()
        # try to load database from disk
        with open(f'{self.db_name}.yaml') as file:
            self.data = yaml.load(file, Loader=yaml.Loader)
            self.items = self.data['items']
            self.hidden_items = self.data['hidden']

    # refreshing views
    def refresh_info(self, idx):
        if self.show_hidden:
            item = self.hidden_items[idx]
        else:
            item = self.items[idx]
        self.info_screen.item_name.text = self.formats.name_format(item['name'])
        self.info_screen.item_time.text = self.formats.time_format(item['time'])
        self.info_screen.item_description.text = self.formats.description_format(item['description'])
        self.info_screen.item_id = idx
        self.info_screen.toggle_view()

    def refresh_view(self):
        if self.show_hidden:
            self.view_screen.items_view.data = self.hidden_items
        else:
            self.view_screen.items_view.data = self.items
        self.view_screen.items_view.refresh_from_data()

    # data manipulations
    def add_item(self, item):
        item = dict(**item)
        item['item_id'] = len(self.items)
        self.items.append(item)

        self.recalculate_max()
        self.refresh_view()
        self.save()

    def add_time(self, idx, value):
        self.items[idx]['time'] += value

        self.recalculate_max()
        self.refresh_view()
        self.refresh_info(idx)
        self.save()

    def remove_item(self, idx):
        self.items.pop(idx)

        self.reindex()
        self.recalculate_max()
        self.refresh_view()
        self.save()

    def recalculate_max(self):
        if len(self.items) != 0:
            max_time = max([x['time'] for x in self.items])
            for x in self.items:
                x['max_time'] = max_time

        if len(self.hidden_items) != 0:
            max_time = max([x['time'] for x in self.hidden_items])
            for x in self.hidden_items:
                x['max_time'] = max_time

    def reindex(self):
        for i, x in enumerate(self.items):
            x['item_id'] = i

        for i, x in enumerate(self.hidden_items):
            x['item_id'] = i

    def save(self):
        """Save database to disk.

        """
        with open(f'{self.db_name}.yaml', 'w') as file:
            yaml.dump(dict(items=self.items,
                           hidden=self.hidden_items), file, Dumper=yaml.Dumper)

    def hide_item(self, idx):
        item = self.items[idx]
        self.remove_item(idx)
        self.hidden_items.append(item)

        self.reindex()
        self.recalculate_max()
        self.refresh_view()
        self.save()

    def unhide_item(self, idx):
        item = self.hidden_items.pop(idx)
        self.add_item(item)

        self.reindex()
        self.recalculate_max()
        self.refresh_view()
        self.save()

    def toggle_view(self):
        self.show_hidden = not self.show_hidden
        self.refresh_view()
        self.info_screen.toggle_view()

