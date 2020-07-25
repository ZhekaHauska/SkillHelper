import yaml
import pandas as pd
from datetime import date, datetime, timedelta
import time
from math import exp

week_days = {'monday': 0,
             'tuesday': 1,
             'wednesday': 2,
             'thursday': 3,
             'friday': 4,
             'saturday': 5,
             'sunday': 6}


class Database:
    def __init__(self, db_name):
        self.show_hidden = False
        # profile
        self.db_name = db_name
        # when your week starts
        self.start_week = week_days['monday']
        # settings
        self.sensitivity = 0.01
        # try to load database from disk
        with open(f'{self.db_name}.yaml') as file:
            self.data = yaml.load(file, Loader=yaml.Loader)

            # self.stats = self.data['stats']
            try:
                self.groups = [x['name'] for x in self.data['groups']]
            except TypeError:
                self.groups = list()

        # try to load history
        try:
            self.history = pd.read_csv(f'{self.db_name}_history.csv', index_col=0, parse_dates=True)
        except FileNotFoundError:
            self.history = pd.DataFrame(columns=['name', 'group', 'time', 'dtime', 'priority'])

    # refreshing
    def refresh_priority(self):
        self.skills_priority()
        self.groups_priority()

    def refresh_groups(self):
        groups = set([x['group'] for x in self.data['skills']['items']])
        for x in self.data['groups']:
            if x['name'] not in groups:
                self.data['groups'].remove(x)
        for x in groups:
            if x not in self.groups:
                self.data['groups'].append({'name': x, 'priority': 0.0})
        self.groups = groups

    # TODO
    # def refresh_stats(self, group=None):
    #     today = time.localtime()
    #
    #     if group is not None:
    #         history = self.history[self.history.group.str.contains(group)]
    #     else:
    #         history = self.history
    #
    #     if today.tm_wday >= self.start_week:
    #         wdays = today.tm_wday - self.start_week
    #     else:
    #         wdays = 7 - (self.start_week - today.tm_wday)
    #     # today
    #     try:
    #         today_summary = history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
    #     except KeyError:
    #         today_summary = 0.0
    #     # week
    #     start = (date.today() - timedelta(days=wdays)).isoformat()
    #     end = date.today().isoformat()
    #     try:
    #         week_summary = history[start: end]['dtime'].sum()
    #     except KeyError:
    #         week_summary = 0.0
    #
    #     if group is not None:
    #         self.stats[group] = {'today': today_summary, 'week': week_summary}
    #     else:
    #         self.stats['total']['today'] = today_summary
    #         self.stats['total']['week'] = week_summary

    # edit data
    def add_item(self, item):
        item = dict(**item)
        item['hidden'] = False
        if len(item['group'].split('/')) == 1:
            self.data['skills']['items'].append(item)
        else:
            self.data['tasks']['items'].append(item)

        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

        self.save()
        
    def edit_item(self, group, name, data, hidden):
        item = self.find_item(group, name, hidden)
        for key, value in data.items():
            item[key] = value

        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

        self.save()
    
    def add_time(self, group, name, value):
        tree = group.split('/')
        tree.append(name)

        for i in range(len(tree)-1, 0, -1):
            g = "/".join(tree[:i])
            self.find_item(g, tree[i])['time'] += value

        self.add_history_entry(self.find_item(group, name), value)

        self.refresh_priority()
        self.sort_items()

        self.save()

    def remove_item(self, group, name, hidden=False):
        g = "/".join([group, name])

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"

        if hidden:
            kindof = 'hidden'
        else:
            kindof = 'items'

        item = self.find_item(group, name, hidden=hidden)
        dependent_items = self.find_item(g, hidden=False)
        dependent_items_h = self.find_item(g, hidden=True)

        self.data[item_type][kindof].remove(item)

        for x in dependent_items:
            self.remove_item(x['group'], x['name'], hidden=False)

        for x in dependent_items_h:
            self.remove_item(x['group'], x['name'], hidden=True)

        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

        self.save()

    def hide_item(self, group, name):
        g = "/".join([group, name])

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"

        item = self.find_item(group, name, hidden=False)
        dependent_items = self.find_item(g, hidden=False)

        self.data[item_type]['items'].remove(item)

        item['hidden'] = True
        self.data[item_type]['hidden'].append(item)

        for x in dependent_items:
            self.hide_item(x['group'], x['name'])

        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

        self.save()

        return item

    def unhide_item(self, group, name):
        g = "/".join([group, name])

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"

        item = self.find_item(group, name, hidden=True)
        dependent_items = self.find_item(g, hidden=True)

        self.data[item_type]['hidden'].remove(item)
        item['hidden'] = False
        self.data[item_type]['items'].append(item)

        for x in dependent_items:
            self.unhide_item(x['group'], x['name'])

        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

        self.save()

        return item

    def sort_items(self):
        self.data['skills']['items'] = sorted(self.data['skills']['items'], key=lambda x: x['priority'], reverse=True)
        self.data['tasks']['items'] = sorted(self.data['tasks']['items'], key=lambda x: x['priority'], reverse=True)
        self.data['groups'] = sorted(self.data['groups'], key=lambda x: x['priority'])

    # priority
    def skills_priority(self):
        # average total for two weeks time
        for x in self.data['skills']['items']:
            if self.history.empty:
                time2w = 0
            else:
                time2w = self.history.query(f'(name == "{x["name"]}") & (group == "{x["group"]}")')['dtime'].resample('14D').sum()
                if not time2w.empty:
                    time2w = time2w.iloc[-1]
                else:
                    time2w = 0
            x['time2w'] = float(time2w)
            dependent = self.get_items('tasks', x['group'] + '/' + x['name'])
            total_priority = 0
            for y in dependent:
                total_priority += self.task_priority(y)
            x['priority'] = exp(-self.sensitivity*time2w) * total_priority * (1 + x['importance'])

    def task_priority(self, task):
        if self.history.empty:
            time2w = 0
        else:
            time2w = self.history.query(f'(name == "{task["name"]}") & (group == "{task["group"]}")')['dtime'].resample(
                '14D').sum()
            if not time2w.empty:
                time2w = time2w.iloc[-1]
            else:
                time2w = 0
        task['time2w'] = float(time2w)

        dependent = self.get_items('tasks', task['group'] + '/' + task['name'])
        total_priority = 0
        for x in dependent:
            total_priority += self.task_priority(x)

        # TODO deadline
        d_time = datetime.strptime(task['deadline'], '%Y-%m-%d %H')
        now = datetime.today()
        dt = ((d_time - now).seconds / 3600) * 0.33
        deadline = task['expected_time'] / (1e-6 + abs(dt))

        priority = deadline*exp(-self.sensitivity*time2w) + total_priority
        task['priority'] = priority
        return priority

    def groups_priority(self):
        for x in self.data['groups']:
            dependent = self.get_items('skills', x['name'])
            total_priority = 0
            for y in dependent:
                total_priority += y['priority']
            x['priority'] = total_priority

    # accessing
    def find_item(self, group, name=None, hidden=False):
        if hidden:
            kindof = 'hidden'
        else:
            kindof = 'items'

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"
        if name is not None:
            for x in self.data[item_type][kindof]:
                if (x['name'] == name) and (x['group'] == group):
                    return x
            else:
                return None
        else:
            res = list()
            for x in self.data[item_type][kindof]:
                if x['group'] == group:
                    res.append(x)
            return res

    def get_items(self, type, group, hidden=False):
        kindof = 'hidden' if hidden else 'items'
        items = filter(lambda x: x['group'] == group, self.data[type][kindof])

        return items

    # history
    def add_history_entry(self, entry, dtime):
        date = pd.to_datetime(time.asctime())
        self.history.loc[date] = [
            entry['name'],
            entry['group'],
            entry['time'],
            dtime,
            entry['priority'],
        ]

    # save
    def save(self):
        """Save database to disk.

        """
        with open(f'{self.db_name}.yaml', 'w') as file:
            yaml.dump(self.data, file, Dumper=yaml.Dumper,
                      allow_unicode=True)

        self.history.to_csv(f'{self.db_name}_history.csv')
