from kivy.uix.recycleview import RecycleView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.slider import Slider
from kivy.properties import NumericProperty, ObjectProperty
from source.widgets import byr_colormap, hsv_to_rgb
from datetime import datetime, timedelta
from kivy.uix.button import Button
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line
from kivy.uix.label import Label
from dateutil.relativedelta import relativedelta
from kivy.clock import Clock


class TaskOverviewItem(BoxLayout):
    pass


class TasksOverview(RecycleView):
    time_scale = NumericProperty(7)

    def __init__(self, **kwargs):
        super(TasksOverview, self).__init__(**kwargs)
        self.data = [dict()]

    def on_time_scale(self, instance, value):
        for item in self.box_layout.children:
            item.time_scale = self.time_scale


class TimelineScreen(Screen):
    def set_time_scale(self, *args):
        self.time_scale.value = 182

    def on_pre_enter(self, *args):
        super(TimelineScreen, self).on_pre_enter(*args)
        self.refresh()

    def on_enter(self, *args):
        super(TimelineScreen, self).on_enter(*args)
        Clock.schedule_once(self.set_time_scale, 0.1)

    def refresh(self):
        data = list()
        for i, item in enumerate(self.manager.database.data['tasks']['items']):
            data.append({'speed': item['expected_average_speed'],
                         'name': item['name'],
                         'days': int(round(item['remain'] / 24)) + 1,
                         'current_days': int(round(item['remain'] / 24)) + 1,
                         'deadline': item['deadline'],
                         'expected_time': item['expected_time'],
                         'group': item['group'],
                         'time_scale': 182,
                         'current_deadline': item['deadline'],
                         'slot_number': i})
        self.tasks.data = data
        self.tasks.refresh_from_data()


class TimeSlider(Slider):
    days = NumericProperty(1)
    speed = ObjectProperty(float(0))

    def __init__(self, **kwargs):
        super(TimeSlider, self).__init__(**kwargs)
        self.expected_speed = 0
        self.deadline = ""

        self.normal_cursor_size = (20, 20)
        self.cursor_size = self.normal_cursor_size
        self.normal_cursor_image = self.cursor_image

        self.min = 1
        self.max = 180
        self.step = 1
        self.value_track = True
        self.value_track_color = (0, 0, 1, 1)

    def on_max(self, instance, value):
        if value < self.days:
            self.value = self.max
            self.cursor_size = (0, 0)
        else:
            self.value = self.days
            self.cursor_size = self.normal_cursor_size
        super(TimeSlider, self).on_max(instance, value)

    def on_days(self, instance, value):
        if value > self.max:
            self.value = self.max
            self.cursor_size = (0, 0)
        elif value < self.min:
            self.value = self.min
            self.cursor_image = "source/edit_cancel.png"
        else:
            self.value = self.days
            self.cursor_size = self.normal_cursor_size
            self.cursor_image = self.normal_cursor_image

    def on_speed(self, instance, value):
        if value > 4:
            v = 1
        else:
            v = value/4
        self.value_track_color = *hsv_to_rgb(*byr_colormap(v)), 1

    def on_value(self, instance, value):
        if self.days < self.max:
            self.speed = self.days * self.expected_speed / (1e-6 + value)
        else:
            self.speed = self.expected_speed

        try:
            deadline = datetime.strptime(self.deadline, '%Y-%m-%d %H')
            current_deadline = deadline + timedelta(days=(value - self.days))
            self.deadline_label.text = current_deadline.strftime('%Y-%m-%d %H')
        except ValueError:
            pass


class ApplyDeadlineButton(Button):
    def on_press(self, *args):
        super(ApplyDeadlineButton, self).on_press(*args)
        for item in self.tasks.box_layout.children:
            if item.deadline != item.deadline_label.text:
                x = self.screen_manager.database.edit_item(item.group,
                                                           item.name,
                                                           {'deadline': item.deadline_label.text},
                                                           False)
        self.info.text = 'All deadlines have saved!'


class TimeScale(RelativeLayout):
    max_days = NumericProperty()

    def on_max_days(self, instance, value):
        disp = 14
        today = datetime.today()
        length = self.width - 2*disp
        height = self.height
        self.canvas.clear()
        scale = None
        if value > 0:
            if value <= 35:
                dt = length / value
                scale = 'day'
            else:
                dt = length / value * 7
                scale = 'month'

            with self.canvas:
                Line(points=[0+disp, height/2 + 5, length+disp, height/2 + 5])
                x = disp
                while x <= length+disp:
                    Line(points=[x, int(height*0.6) + 5, x, int(0.4*height) + 5])
                    x += dt

            if scale == 'day':
                x = disp
                d = 0
                while x <= length + disp:
                    self.add_widget(Label(pos=(0-self.width/2 + x + dt/2, 0-height*0.2/2),
                                          size=(dt*0.9, int(height*0.2)),
                                          text=(today + timedelta(days=d)).strftime('%a'),
                                          font_size=9))
                    x += dt
                    d += 1
            else:
                dt = length / value
                prev_month = today
                x = 0
                while x <= length + disp:
                    next_month = prev_month + relativedelta(months=+1)
                    next_month = next_month.replace(day=1)
                    x = disp + (prev_month - today).days * dt + (next_month - prev_month).days/2 * dt
                    self.add_widget(Label(pos=(0 - self.width / 2 + x + dt / 2, 0 - height * 0.2 / 2),
                                          size=(dt * 0.9, int(height * 0.2)),
                                          text=prev_month.strftime('%b'),
                                          font_size=9))
                    prev_month = next_month







