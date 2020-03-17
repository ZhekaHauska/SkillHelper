import yaml
import pandas as pd
import time


week_days = {'monday': 0,
             'tuesday': 1,
             'wednesday': 2,
             'thursday': 3,
             'friday': 4,
             'saturday': 5,
             'sunday': 6}


class Formats:
    def name_format(self, name):
        return name

    def time_format(self, time):
        return f"Total time: {round(time, 2)} hours"

    def description_format(self, description):
        return description


class Database:
    def __init__(self, db_name, view_screen, info_screen, edit_screen):
        self.db_name = db_name
        # when your week starts
        self.start_week = week_days['monday']
        self.show_hidden = False
        self.view_screen = view_screen
        self.info_screen = info_screen
        self.edit_screen = edit_screen
        self.formats = Formats()
        # try to load database from disk
        with open(f'{self.db_name}.yaml') as file:
            self.data = yaml.load(file, Loader=yaml.Loader)
            self.items = self.data['items']
            self.hidden_items = self.data['hidden']
        # try to load history
        try:
            self.history = pd.read_csv('history.csv', index_col=0, parse_dates=True)
        except FileNotFoundError:
            self.history = pd.DataFrame(columns=['name', 'type', 'time', 'importance', 'dtime'])
        # calculate expected time
        # average total for two weeks time
        self.expected_time = self.history['dtime'].resample('14D').sum().mean()
        if self.expected_time == 0:
            self.expected_time = 6*14

        self.recalculate_priority()
        self.sort_items()

    # refreshing views
    def refresh_edit(self, idx):
        item = self.items[idx]
        self.edit_screen.item_name.text = str(item['name'])
        self.edit_screen.item_time.text = str(item['time'])
        self.edit_screen.item_description.text = item['description']
        self.edit_screen.item_importance.value = item['importance']
        self.edit_screen.curr_item = item

    def refresh_info(self, idx):
        if self.show_hidden:
            item = self.hidden_items[idx]
        else:
            item = self.items[idx]
        self.info_screen.item_name.text = self.formats.name_format(item['name'])
        self.info_screen.item_time.text = self.formats.time_format(item['time'])
        self.info_screen.item_description.text = self.formats.description_format(item['description'])
        self.info_screen.curr_item = item
        self.info_screen.toggle_view()

    def refresh_view(self):
        if self.show_hidden:
            self.view_screen.items_view.data = self.hidden_items
        else:
            self.view_screen.items_view.data = self.items
        self.view_screen.items_view.refresh_from_data()

    def refresh_stats(self):
        today = time.localtime()
        if today.tm_wday >= self.start_week:
            wdays = today.tm_wday - self.start_week
        else:
            wdays = 7 - (self.start_week - today.tm_wday)
        # today
        try:
            today_summary = self.history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
        except KeyError:
            today_summary = 0.0
        # week
        try:
            week_summary = self.history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday - wdays}':
                                    f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
        except KeyError:
            week_summary = 0.0
        self.view_screen.stats.text = 'Today: {} hours  This week: {} hours'.format(today_summary, week_summary)

    # data manipulations
    def add_item(self, item):
        item = dict(**item)
        item['item_id'] = len(self.items)
        self.items.append(item)

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()

        self.refresh_view()
        self.save()
        
    def edit_item(self, item, idx):
        self.items[idx] = item

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()

        self.refresh_view()
        self.save()
    
    def add_time(self, idx, value):
        self.items[idx]['time'] += value
        self.add_history_entry(idx, value)
        self.refresh_info(idx)
        self.refresh_stats()

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()

        self.refresh_view()
        self.save()

    def remove_item(self, idx):
        self.items.pop(idx)

        self.recalculate_priority()
        self.sort_items()
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

        self.history.to_csv('history.csv')

    def hide_item(self, idx):
        item = self.items[idx]
        self.remove_item(idx)
        self.hidden_items.append(item)

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.refresh_view()
        self.save()

    def unhide_item(self, idx):
        item = self.hidden_items.pop(idx)
        self.add_item(item)

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.refresh_view()
        self.save()

    def toggle_view(self):
        self.show_hidden = not self.show_hidden
        self.refresh_view()
        self.info_screen.toggle_view()

    def recalculate_priority(self):
        total_importance = 0
        for x in self.items:
            total_importance += (x['importance'] + 1)

        for x in self.items:
            etime = (x['importance'] + 1) * self.expected_time / total_importance
            priority = 1 - x['time'] / etime
            x['priority'] = priority

    def sort_items(self):
        self.items = sorted(self.items, key=lambda x: x['priority'], reverse=True)
        self.reindex()

    def add_history_entry(self, idx, dtime):
        entry = self.items[idx]
        date = pd.to_datetime(time.asctime())
        self.history.loc[date] = [
            entry['name'],
            self.db_name,
            entry['time'],
            entry['importance'],
            dtime
        ]


class SkillsDatabase(Database):
    def refresh_info(self, idx):
        pass

    def recalculate_priority(self):
        pass


class TasksDatabase(Database):
    def refresh_info(self, idx):
        pass
