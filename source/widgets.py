from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Line, Color
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.slider import Slider
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors import DragBehavior
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.graphics import Triangle, Ellipse, Rectangle, RoundedRectangle
from kivy.uix.bubble import Bubble, BubbleButton
from kivy.uix.scatter import ScatterPlane
from kivy.uix.recycleview import RecycleView
from kivy.uix.button import Button
import numpy as np
import math


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
    # value - float between 0 and 1
    if value < 0.5:
        color = (2*value, 2*value, (0.5 - value)*2)
    else:
        color = (1, (1 - value)*2, 0)

    color = rgb_to_hsv(*color)
    color = (color[0], saturation, 1)
    return color


class ColoredIndicator(AnchorLayout):
    val = ObjectProperty(float(0))

    def byr_colormap(self, value, saturation=0.8):
        # value - float between 0 and 1
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
            sm = self.parent.parent.screen_manager

            sm.skill_info_screen.item = sm.database.find_item(self.group, self.name, self.hidden)
            sm.current = 'skill_info_screen'

            return True
        return super(SkillItem, self).on_touch_up(touch)


class TaskItem(Item):
    def on_touch_up(self, touch):
        if self.selected:
            self.canvas.remove(self.selected)
            self.selected = None
            sm = self.parent.parent.screen_manager

            sm.task_info_screen.item = sm.database.find_item(self.group, self.name, self.hidden)
            sm.current = 'task_info_screen'

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


class NodeEditor(ScatterPlane):
    def __init__(self, screen_manager, **kwargs):
        super(NodeEditor, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.add_bubble = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.is_double_tap:
                self.show_bubble(*self.to_local(*touch.pos))
        super(NodeEditor, self).on_touch_down(touch)

    def show_bubble(self, x, y):
        if self.add_bubble is not None:
            self.remove_widget(self.add_bubble)
            self.add_bubble = None
        self.data = self.screen_manager.database.data
        self.add_bubble = AddNodeBubble(self.data)
        self.add_bubble.pos = (x - self.add_bubble.width/2, y)
        self.add_widget(self.add_bubble)


class AddNodeBubble(Bubble):
    def __init__(self, data, **kwargs):
        super(AddNodeBubble, self).__init__(**kwargs)
        self.data = data
        self.skill_button = BubbleButton(text="skill")
        self.skill_button.bind(on_press=self.show_skills_view)
        self.add_widget(self.skill_button)

    def show_skills_view(self, instance):
        self.remove_widget(self.skill_button)
        self.height *= 2
        self.width *= 1.2
        self.add_widget(NodesView(self.data['skills']['items'], "skill"))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos) and not touch.is_double_tap:
            self.parent.add_bubble = None
            self.parent.remove_widget(self)
        super(AddNodeBubble, self).on_touch_down(touch)


class NodesView(RecycleView):
    def __init__(self, data, type, **kwargs):
        super(NodesView, self).__init__(**kwargs)
        self.viewclass = "NodeItem"
        self.data = data
        self.type = type


class Node(Label):
    state = ObjectProperty("normal")

    def __init__(self, type, group, name, **kwargs):
        self.type = type
        self.group = group
        self.name = name
        if self.type == "skill":
            self.h_color = (0.7, 0.8, 1)
        elif self.type == "task":
            self.h_color = (0.3, 0.8, 1)
        else:
            self.h_color = (0.5, 0.8, 1)
        super(Node, self).__init__(**kwargs)
        self.connected = list()
        self.connections = list()
        self.bubble = None
        self.selected = None
        self.ix = self.x
        self.iy = self.y

    def on_touch_down(self, touch):
        if self.widget_collide(*touch.pos):
            for child in self.parent.children:
                if isinstance(child, Node):
                    if child.state == "connect":
                        super(Node, self).on_touch_down(touch)
                        break
            else:
                if self.bubble is None:
                    self.bubble = NodeBubble(self)
                    self.bubble.pos_hint = (None, None)
                    self.bubble.x = touch.x - self.bubble.width / 2
                    self.bubble.y = touch.y
                    self.parent.add_widget(self.bubble)
                    return True
        elif self.state == "connect":
            (x, y) = self.to_parent(*touch.pos)
            for child in self.parent.children:
                if child.collide_point(x, y) and isinstance(child, Node) and child not in self.connected and child is not self:
                    self.state = "normal"
                    connection = Connection(self, child)
                    self.parent.add_widget(connection, index=100)
                    self.connections.append(connection)
                    child.connections.append(connection)
                    self.connected.append(child)
                    child.connected.append(self)
                    return True
            else:
                self.state = "normal"
                super(Label, self).on_touch_down(touch)
        elif self.handle_collide(*touch.pos):
            self.ix = touch.x
            self.iy = touch.y
            self.state = "drag"
            return True
        else:
            if self.bubble is not None:
                self.parent.remove_widget(self.bubble)
                self.bubble = None
            super(Label, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.state == "drag":
            self.x += touch.x - self.ix
            self.y += touch.y - self.iy
            self.ix += touch.x - self.ix
            self.iy += touch.y - self.iy
        super(Node, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.state == "drag":
            self.state = "normal"
        super(Node, self).on_touch_up(touch)

    def on_state(self, instance, value):
        if self.state == "connect":
            with self.canvas.before:
                Color(rgb=(1, 1, 1))
                self.selected = RoundedRectangle(pos=(self.x - 5, self.y - 5), size=(self.width + 10, self.height + 10))
        elif self.state == "normal":
            if self.selected is not None:
                self.canvas.before.remove(self.selected)
                self.selected = None
        elif self.state == "drag":
            if self.selected is not None:
                self.canvas.before.remove(self.selected)
                self.selected = None

    def handle_collide(self, x, y):
        if self.x < x < self.x + self.width:
            if self.y + self.height - self.handle_height < y < self.y + self.height:
                return True

    def widget_collide(self, x, y):
        if self.x < x < self.x + self.width:
            if self.y < y < self.y + self.height - self.handle_height:
                return True


class Connection(RelativeLayout):
    direction = NumericProperty(0)
    strength = ObjectProperty(float(0))

    def __init__(self, node1, node2, **kwargs):
        super(Connection, self).__init__(**kwargs)
        self.arrow_l = 20
        self.arrow_w = 10
        self.max_line_width = 5
        self.line = None
        self.arrow = None
        self.points = None
        self.bubble = None
        self.point1 = dict(x=node1.center_x, y=node1.center_y)
        self.point2 = dict(x=node2.center_x, y=node2.center_y)
        self.node1 = node1
        self.node2 = node2
        self.redraw()

    def redraw(self):
        if self.line is not None:
            self.canvas.before.remove(self.line)
        if self.arrow is not None:
            self.canvas.before.remove(self.arrow)
        self.points = x1, y1, x2, y2, x3, y3 = self.arrow_points()
        with self.canvas.before:
            self.line = Line(points=[self.point1['x'], self.point1['y'],
                                     self.point2['x'], self.point2['y']], width=self.strength*self.max_line_width)
            if self.direction == 2:
                self.arrow = Ellipse(pos=(x1 - self.arrow_w, y1 - self.arrow_w), size=(self.arrow_w*2, self.arrow_w*2))
                self.points = (x1 - self.arrow_w, y1 - self.arrow_w, x1 + self.arrow_w, y1 + self.arrow_w*2)
            else:
                self.arrow = Triangle(points=[x1, y1, x2, y2, x3, y3])

    def on_touch_move(self, touch):
        if self.node1.state == "drag" or self.node2.state == "drag":
            self.point1 = dict(x=self.node1.center_x, y=self.node1.center_y)
            self.point2 = dict(x=self.node2.center_x, y=self.node2.center_y)
            self.redraw()
        super(RelativeLayout, self).on_touch_move(touch)

    def arrow_points(self):
        a1 = np.array([self.point2['x'], self.point2['y']])
        a2 = np.array([self.point1['x'], self.point1['y']])
        if self.direction == 1:
            a1, a2 = a2, a1
        a3 = a1 + 0.5 * (a2 - a1)
        a6 = a1 + (0.5 + self.arrow_l/np.linalg.norm(a2-a1)) * (a2 - a1)
        k = a6 - a1
        k = k[1] / k[0]

        y5 = a6[1] + self.arrow_w / math.sqrt(1 + k*k)
        y7 = a6[1] - self.arrow_w / math.sqrt(1 + k*k)
        if math.fabs(k) == math.inf:
            x5 = a6[0] + self.arrow_w
            x7 = a6[0] - self.arrow_w
        else:
            x5 = a6[0] - (y5 - a6[1]) * k
            x7 = a6[0] - (y7 - a6[1]) * k
        # print(a3, x5, y5, x7, y7, k, a6, a1, a2)
        return int(a3[0]), int(a3[1]), int(x5), int(y5), int(x7), int(y7)

    def on_touch_down(self, touch):
        if self.collide_bbox(*touch.pos):
            if self.bubble is None:
                self.bubble = ConnectBubble(self)
                self.bubble.pos_hint = (None, None)
                self.bubble.x = touch.x - self.bubble.width / 2
                self.bubble.y = touch.y
                self.parent.add_widget(self.bubble)
        else:
            self.parent.remove_widget(self.bubble)
            self.bubble = None
        super(RelativeLayout, self).on_touch_down(touch)

    def on_direction(self, instance, value):
        self.redraw()

    def on_strength(self, instance, value):
        self.redraw()

    def collide_bbox(self, x, y):
        px = self.points[::2]
        py = self.points[1::2]
        bbox = min(px), min(py), max(px), max(py)
        return (bbox[0] < x < bbox[2]) and (bbox[1] < y < bbox[3])


class ConnectBubble(Bubble):
    def __init__(self, connection, **kwargs):
        super(ConnectBubble, self).__init__(**kwargs)
        self.connection = connection


class NodeBubble(Bubble):
    def __init__(self, node, **kwargs):
        super(NodeBubble, self).__init__(**kwargs)
        self.node = node

    def remove_node(self):
        for connection in self.node.connections:
            if self.node is connection.node2:
                connection.node1.connected.remove(self.node)
                connection.node1.connections.remove(connection)
            else:
                connection.node2.connected.remove(self.node)
                connection.node2.connections.remove(connection)
            self.parent.remove_widget(connection)
        self.parent.remove_widget(self.node)
        self.parent.remove_widget(self)


class Handle(Widget):
    pass


class NodeItem(BubbleButton):
    def on_press(self):
        node = Node(type=self.parent.parent.type, group=self.group, name=self.name)
        node.text = self.group + '/' + self.name
        node.pos = self.parent.parent.parent.parent.pos
        self.parent.parent.parent.parent.parent.add_widget(node, index=0)
        super(NodeItem, self).on_press()


class EditableLabel(RelativeLayout):
    text = ObjectProperty()

    def __init__(self, **kwargs):
        self.label = Label()
        self.input = None
        self.screen = None
        super(EditableLabel, self).__init__(**kwargs)

        self.add_widget(self.label)

    def on_text(self, *args):
        self.label.text = self.text

    def apply(self, *args):
        # default
        self.text = self.input.text
        self.remove_widget(self.input)
        self.add_widget(self.label)

    def cancel(self, instance, value):
        if not value:
            self.remove_widget(self.children[0])
            self.add_widget(self.label)

    def focus(self, *args):
        self.children[0].focus = True

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            if self.collide_point(*touch.pos):
                self.input = TextInput(text=self.text, multiline=False, halign='center',
                                       valign='center')
                self.input.bind(on_text_validate=self.apply)
                self.input.bind(focus=self.cancel)

                self.remove_widget(self.label)

                self.add_widget(self.input)
                Clock.schedule_once(self.focus, 0.5)

        super(EditableLabel, self).on_touch_down(touch)


class DeadlineLabel(EditableLabel):
    def apply(self, *args):
        super(DeadlineLabel, self).apply(*args)
        self.screen.save({'deadline': self.text})


class ExpectedTimeLabel(EditableLabel):
    def apply(self, *args):
        super(ExpectedTimeLabel, self).apply(*args)
        self.screen.save({'expected_time': float(self.text)})
