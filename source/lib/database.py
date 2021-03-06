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
        # profile
        self.db_name = db_name
        # when your week starts
        self.start_week = week_days['monday']
        # settings
        self.sensitivity = 0.01
        # try to load database from disk
        try:
            file = open(f'{self.db_name}.yaml', 'r')
            self.data = yaml.load(file, Loader=yaml.Loader)
            file.close()
        except FileNotFoundError:
            self.data = {'groups': [],
                         'skills': {'hidden': [], 'items': []},
                         'tasks': {'hidden': [], 'items': []}
                         }
        try:
            self.groups = [x['name'] for x in self.data['groups']]
        except TypeError:
            self.groups = list()

        # try to load history
        try:
            self.history = pd.read_csv(f'{self.db_name}_history.csv', index_col=0, parse_dates=True)
        except FileNotFoundError:
            self.history = pd.DataFrame(columns=['name', 'group', 'time', 'dtime', 'priority'])

        # stats
        self.stats = dict()
        # initialize
        self.refresh_groups()
        self.refresh_priority()
        self.sort_items()

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
        self.groups = list(groups)

    def refresh_stats(self, group=None, name=None):
        today = time.localtime()

        if group is not None:
            if name is None:
                history = self.history[self.history.group.str.contains(group)]
            else:
                history = self.history[self.history.group.str.contains(group) & self.history.name.str.contains(name)]
        else:
            history = self.history

        if today.tm_wday >= self.start_week:
            wdays = today.tm_wday - self.start_week
        else:
            wdays = 7 - (self.start_week - today.tm_wday)
        # today
        try:
            today_summary = history[f'{today.tm_year}-{today.tm_mon}-{today.tm_mday}']['dtime'].sum()
        except KeyError:
            today_summary = 0.0
        # week
        start = (date.today() - timedelta(days=wdays)).isoformat()
        end = date.today().isoformat()
        try:
            week_summary = history[start: end]['dtime'].sum()
        except KeyError:
            week_summary = 0.0

        if group is not None:
            if name is None:
                self.stats[group] = {'today': today_summary, 'week': week_summary}
        else:
            self.stats['total'] = {'today': today_summary, 'week': week_summary}

        return {'today': today_summary, 'week': week_summary}

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
        self.data['groups'] = sorted(self.data['groups'], key=lambda x: x['priority'], reverse=True)
        self.groups = [x['name'] for x in self.data['groups']]

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
            total_exp_speed = 0
            total_speed = 0
            for y in dependent:
                total_priority += self.task_priority(y)
                total_exp_speed += y['expected_average_speed']
                total_speed += y['average_speed']
            x['priority'] = exp(-self.sensitivity*time2w) * total_priority * (1 + x['importance'])
            x['expected_speed'] = total_exp_speed
            x['speed'] = total_speed

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

        d_time = datetime.strptime(task['deadline'], '%Y-%m-%d %H')
        now = datetime.today()
        dt = (d_time - now).total_seconds() / 3600
        deadline = task['expected_time'] / (1e-6 + abs(dt))
        # average speed
        # for compatibility
        try:
            started = datetime.strptime(task['started'], '%Y-%m-%d %H')
        except KeyError:
            task['started'] = "2020-07-26 12"
            started = datetime.strptime(task['started'], '%Y-%m-%d %H')
        # hours per day
        av_speed = task['time'] / (int(((now - started).total_seconds()) / (3600 * 24)) + 1)
        if ((d_time - now).total_seconds() < 0) or (task['expected_time'] < task['time']):
            exp_speed = 0
        else:
            exp_speed = (task['expected_time'] - task['time']) / (
                        int(((d_time - now).total_seconds()) / (3600 * 24)) + 1)

        if exp_speed < 0.1:
            priority = deadline + total_priority
        else:
            priority = deadline*(exp_speed / (1e-6 + av_speed)) + total_priority
        task['average_speed'] = av_speed
        task['expected_average_speed'] = exp_speed
        task['priority'] = priority
        task['remain'] = dt
        return priority

    def groups_priority(self):
        for x in self.data['groups']:
            dependent = self.get_items('skills', x['name'])
            total_priority = 0
            total_exp_speed = 0
            total_speed = 0
            for y in dependent:
                total_priority += y['priority']
                total_exp_speed += y['expected_speed']
                total_speed += y['speed']
            x['priority'] = total_priority
            x['expected_speed'] = total_exp_speed
            x['speed'] = total_speed

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
