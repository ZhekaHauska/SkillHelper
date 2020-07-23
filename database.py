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
        self.show_hidden = False
        # profile
        self.db_name = db_name
        # when your week starts
        self.start_week = week_days['monday']
        # settings
        self.sensitivity = 1.2
        # try to load database from disk
        with open(f'{self.db_name}.yaml') as file:
            self.data = yaml.load(file, Loader=yaml.Loader)

            self.stats = self.data['stats']
            self.groups = self.data['groups']
            self.expected_time = self.data['expected_time']

        # try to load history
        try:
            self.history = pd.read_csv(f'{self.db_name}_history.csv', index_col=0, parse_dates=True)
        except FileNotFoundError:
            self.history = pd.DataFrame(columns=['name', 'time', 'importance', 'dtime', 'group'])

    # refreshing
    def refresh_groups(self):
        self.groups = set([x['group'] for x in self.data['skills']['items']])

    def refresh_stats(self, group=None):
        today = time.localtime()

        if group is not None:
            history = self.history[self.history.group.str.contains(group)]
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
            self.stats[group] = {'today': today_summary, 'week': week_summary}
        else:
            self.stats['total']['today'] = today_summary
            self.stats['total']['week'] = week_summary

    # data manipulations
    def add_item(self, item):
        item = dict(**item)
        if len(item['group'].split('/')) == 1:
            self.data['tasks']['items'].append(item)
        else:
            self.data['tasks']['items'].append(item)

        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()
        self.refresh_groups()

        self.save()
        
    def edit_item(self, group, name, item):
        # TODO edit item
        self.recalculate_max()
        self.recalculate_priority()
        self.sort_items()
        self.refresh_groups()

        self.save()
    
    def add_time(self, group, name, value):
        tree = group.split('/')
        tree.append(name)

        for i in range(len(tree)-1, 0, -1):
            g = "/".join(tree[:i])
            self.find_item(g, tree[i])['time'] += value

        self.add_history_entry(self.find_item(group, name), value)

        self.recalculate_max()
        self.recalculate_priority()
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

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()
        self.refresh_groups()

        self.save()

    def recalculate_max(self):
        # TODO
        if len(self.data['skills']['items']) != 0:
            max_time = max([x['time'] for x in self.data['skills']['items']])
            for x in self.data['skills']['items']:
                x['max_time'] = max_time

        if len(self.data['skills']['hidden']) != 0:
            max_time = max([x['time'] for x in self.data['skills']['hidden']])
            for x in self.data['skills']['hidden']:
                x['max_time'] = max_time

    def save(self):
        """Save database to disk.

        """
        with open(f'{self.db_name}.yaml', 'w') as file:
            yaml.dump(self.data, file, Dumper=yaml.Dumper,
                      allow_unicode=True)

        self.history.to_csv(f'{self.db_name}_history.csv')

    def hide_item(self, group, name):
        g = "/".join([group, name])

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"

        item = self.find_item(group, name, hidden=False)
        dependent_items = self.find_item(g, hidden=False)

        self.data[item_type]['hidden'].append(item)
        self.data[item_type]['items'].remove(item)

        for x in dependent_items:
            self.hide_item(x['group'], x['name'])

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.save()

    def unhide_item(self, group, name):
        g = "/".join([group, name])

        if len(group.split('/')) == 1:
            item_type = "skills"
        else:
            item_type = "tasks"

        item = self.find_item(group, name, hidden=True)
        dependent_items = self.find_item(g, hidden=True)

        self.data[item_type]['items'].append(item)
        self.data[item_type]['hidden'].remove(item)

        for x in dependent_items:
            self.unhide_item(x['group'], x['name'])

        self.recalculate_priority()
        self.sort_items()
        self.recalculate_max()

        self.save()

    def recalculate_priority(self):
        pass
        # calculate expected time
        # average total for two weeks time
        # if self.history.empty:
        #     self.expected_time = 3 * 14
        # else:
        #     self.expected_time = self.history['dtime'].resample('14D').sum().mean()
        #
        # total_importance = 0
        # for x in self.skills:
        #     total_importance += pow(self.sensitivity, x['importance'])
        #
        # for x in self.skills:
        #     if self.history.empty:
        #         time2w = 0
        #     else:
        #         time2w = self.history.query(f'name == "{x["name"]}"')['dtime'].resample('14D').sum()
        #         if not time2w.empty:
        #             time2w = time2w.iloc[-1]
        #         else:
        #             time2w = 0
        #     etime = pow(self.sensitivity, x['importance']) * self.expected_time / total_importance
        #     priority = 1 - time2w / etime
        #     x['priority'] = float(priority)
        #     x['etime'] = float(etime)
        #     x['time2w'] = float(time2w)

    def sort_items(self):
        pass
        # TODO
        # self.data['skills'] = sorted(self.skills, key=lambda x: x['priority'], reverse=True)

    def add_history_entry(self, entry, dtime):
        date = pd.to_datetime(time.asctime())
        self.history.loc[date] = [
            entry['name'],
            entry['time'],
            entry['importance'],
            dtime,
            entry['group']
        ]

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
