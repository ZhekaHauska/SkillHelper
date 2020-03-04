from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color
from kivy.uix.textinput import TextInput


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
        return super(SHTextInput, self).on_touch_down(touch)
