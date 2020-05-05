import yaml
import pandas as pd
from datetime import date, timedelta
import time

week_days = {'monday': 0,
             'tuesday': 1,
             'wednesday': 2,
             'thursday': 3,
             'friday': 4,
             'saturday': 5,
             'sunday': 6}


class Database:
    def __init__(self, db_name):
        # profile
        self.db_name = db_name
        # when your week starts
        self.start_week = week_days['monday']
        # state
        self.current_group = None
        self.show_hidden = False
        # settings
        self.sensitivity = 1.2
        # try to load database from disk
        with open(f'{self.db_name}.yaml') as file:
            self.data = yaml.load(file, Loader=yaml.Loader)

            self.data_skills = self.data['skills']
            self.skills = self.data_skills['items']
            self.hidden_skills = self.data_skills['hidden']
            self.expected_time = self.data_skills['expected_time']

            self.data_tasks = self.data['tasks']
            self.tasks = self.data_tasks['items']
            self.hidden_tasks = self.data_tasks['hidden']
            self.expected_time = self.data_tasks['expected_time']

            self.stats = self.data['stats']
            self.groups = self.data['groups']

        # try to load history
        try:
            self.history = pd.read_csv(f'{self.db_name}_history.csv', index_col=0, parse_dates=True)
        except FileNotFoundError:
            self.history = pd.DataFrame(columns=['name', 'time', 'importance', 'dtime', 'group'])

    # refreshing
    def refresh_groups(self):
        self.groups = set([x['group'] for x in self.skills])

    def refresh_stats(self):
        today = time.localtime()
        cgroup_history = self.history.query(f'group == "{self.current_group}"')
        if today.tm_wday >= self.start_week:
            wdays = today.tm_wday - self.start_week
        else:
            wdays = 7 - (self.start_week - today.tm_wday)
        # today
        try:
            today_full_summary = self.history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
            today_group_summary = cgroup_history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
        except KeyError:
            today_full_summary = 0.0
            today_group_summary = 0.0
        # week
        start = (date.today() - timedelta(days=wdays)).isoformat()
        end = date.today().isoformat()
        try:
            week_full_summary = self.history[start:
                                             end]['dtime'].sum()
            week_group_summary = cgroup_history[start:
                                                end]['dtime'].sum()
        except KeyError:
            week_full_summary = 0.0
            week_group_summary = 0.0

        self.stats = dict(today_full_summary=today_full_summary,
                          today_group_summary=today_group_summary,
                          week_full_summary=week_full_summary,
                          week_group_summary=week_group_summary)

    # data manipulations
    def add_item(self, item):
        item = dict(**item)
        item['item_id'] = len(self.skills)
        self.skills.append(item)

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()
        self.refresh_groups()

        self.save()
        
    def edit_item(self, item, idx):
        self.skills[idx] = item

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()
        self.refresh_groups()

        self.save()
    
    def add_time(self, idx, value):
        self.skills[idx]['time'] += value
        self.add_history_entry(idx, value)

        self.refresh_stats()
        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()

        self.save()

    def remove_item(self, idx):
        self.skills.pop(idx)

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()
        self.refresh_groups()

        self.save()

    def recalculate_max(self):
        if len(self.skills) != 0:
            max_time = max([x['time'] for x in self.skills])
            for x in self.skills:
                x['max_time'] = max_time

        if len(self.hidden_skills) != 0:
            max_time = max([x['time'] for x in self.hidden_skills])
            for x in self.hidden_skills:
                x['max_time'] = max_time

    def reindex(self):
        for i, x in enumerate(self.skills):
            x['item_id'] = i

        for i, x in enumerate(self.hidden_skills):
            x['item_id'] = i

    def save(self):
        """Save database to disk.

        """
        with open(f'{self.db_name}.yaml', 'w') as file:
            yaml.dump(self.data, file, Dumper=yaml.Dumper,
                      allow_unicode=True)

        self.history.to_csv(f'{self.db_name}_history.csv')

    def hide_item(self, idx):
        item = self.skills[idx]
        self.remove_item(idx)
        self.hidden_skills.append(item)

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.save()

    def unhide_item(self, idx):
        item = self.hidden_skills.pop(idx)
        self.add_item(item)

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.save()

    def toggle_view(self):
        self.show_hidden = not self.show_hidden

    def recalculate_priority(self):
        # calculate expected time
        # average total for two weeks time
        if self.history.empty:
            self.expected_time = 3 * 14
        else:
            self.expected_time = self.history['dtime'].resample('14D').sum().mean()

        total_importance = 0
        for x in self.skills:
            total_importance += pow(self.sensitivity, x['importance'])

        for x in self.skills:
            if self.history.empty:
                time2w = 0
            else:
                time2w = self.history.query(f'name == "{x["name"]}"')['dtime'].resample('14D').sum()
                if not time2w.empty:
                    time2w = time2w.iloc[-1]
                else:
                    time2w = 0
            etime = pow(self.sensitivity, x['importance']) * self.expected_time / total_importance
            priority = 1 - time2w / etime
            x['priority'] = float(priority)
            x['etime'] = float(etime)
            x['time2w'] = float(time2w)

    def sort_items(self):
        self.skills = sorted(self.skills, key=lambda x: x['priority'], reverse=True)
        self.reindex()

    def add_history_entry(self, idx, dtime):
        entry = self.skills[idx]
        date = pd.to_datetime(time.asctime())
        self.history.loc[date] = [
            entry['name'],
            entry['time'],
            entry['importance'],
            dtime,
            entry['group']
        ]

    def find_item(self, name):
        for x in self.skills:
            if x['name'] == name:
                return x['item_id']
        else:
            return None
