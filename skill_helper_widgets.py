from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.uix.slider import Slider


def hsv_to_rgb(h, s, v):
    h *= 360
    c = v * s
    hs = h / 60
    x = c * (1 - abs(hs % 2 - 1))
    if 0 <= hs <= 1:
        r, g, b = c, x, 0
    elif 1 < hs <= 2:
        r, g, b = x, c, 0
    elif 2 < hs <= 3:
        r, g, b = 0, c, x
    elif 3 < hs <= 4:
        r, g, b = 0, x, c
    elif 4 < hs <= 5:
        r, g, b = x, 0, c
    elif 5 < hs <= 6:
        r, g, b = c, 0, x
    else:
        r, g, b = 0, 0, 0

    m = v - c
    r, g, b = r + m, g + m, b + m
    return r, g, b


def rgb_to_hsv(r, g, b):
    r = float(r)
    g = float(g)
    b = float(b)
    high = max(r, g, b)
    low = min(r, g, b)

    v = high

    if high == 0:
        s = 0
    else:
        s = 1 - low / high

    if high == low:
        h = 0
    elif high == r and g >= b:
        h = 60 * (g - b) / (high - low)
    elif high == r and g < b:
        h = 60 * (g - b) / (high - low) + 360
    elif high == g:
        h = 60 * (b - r) / (high - low) + 120
    else:
        h = 60 * (r - g) / (high - low) + 240

    h /= 360
    return h, s, v


def byr_colormap(value, saturation=0.8):
    if value < 0.5:
        color = (2*value, 2*value, (0.5 - value)*2)
    else:
        color = (1, (1 - value)*2, 0)

    color = rgb_to_hsv(*color)
    color = (color[0], saturation, color[2])
    return color


class ColoredIndicator(AnchorLayout):
    val = ObjectProperty(float(0))

    def byr_colormap(self, value, saturation=0.8):
        if value < 0.5:
            color = (2*value, 2*value, (0.5 - value)*2)
        else:
            color = (1, (1 - value)*2, 0)

        color = rgb_to_hsv(*color)
        color = (color[0], saturation, color[2])
        return color


class Item(BoxLayout):
    def __init__(self, **kwargs):
        self.selected = None
        super(Item, self).__init__(**kwargs)

    def on_touch_down(self, touch):
        if self.collide_point(touch.x, touch.y):
            with self.canvas:
                Color(1, 1, 1)
                x, y = self.to_parent(0, 0, relative=True)
                self.selected = Line(rectangle=(x, y, self.width, self.height), dash_offset=2)
            return True
        return super(Item, self).on_touch_down(touch)


class SkillItem(Item):
    def on_touch_up(self, touch):
        if self.selected:
            self.canvas.remove(self.selected)
            self.selected = None
            self.parent.parent.screen_manager.current = 'skill_info_screen'
            self.parent.parent.screen_manager.db_skills.refresh_info(self.item_id)
            return True
        return super(SkillItem, self).on_touch_up(touch)


class TaskItem(Item):
    def on_touch_up(self, touch):
        if self.selected:
            self.canvas.remove(self.selected)
            self.selected = None
            self.parent.parent.screen_manager.current = 'task_info_screen'
            self.parent.parent.screen_manager.db_tasks.refresh_info(self.item_id)
            return True
        return super(TaskItem, self).on_touch_up(touch)


class SHTextInput(TextInput):
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.select_all()
        return super(SHTextInput, self).on_touch_up(touch)


class Timer(BoxLayout):
    def __init__(self, **kwargs):
        super(Timer, self).__init__(**kwargs)
        self.time = 0
        self.state = "off"

    def start(self):
        self.time = 0
        self.state = "on"
        Clock.schedule_interval(self.refresh_timer, 1)

    def refresh_timer(self, dt):
        if self.state == "on":
            self.time += 1
            self.timer.text = "{} : {} : {}".format(self.time // 3600,
                                                    (self.time % 3600) // 60,
                                                     self.time % 60)
        elif self.state == "pause":
            pass
        else:
            return False

    def finish(self):
        self.state = "off"
        self.add_time_amount.text = str(round(self.time / 3600, 2))

    def pause(self):
        if self.state == "pause":
            self.state = "on"
        elif self.state == "on":
            self.state = "pause"


class ImportanceSlider(Slider):
    def on_value(self, instance, value):
        self.value_track_color = *hsv_to_rgb(*byr_colormap(value)), 1
