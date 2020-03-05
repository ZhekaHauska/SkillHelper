from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color
from kivy.uix.textinput import TextInput
from kivy.clock import Clock


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
