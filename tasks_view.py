from kivy.uix.recycleview import RecycleView


class TasksView(RecycleView):
    def __init__(self, **kwargs):
        super(TasksView, self).__init__(**kwargs)
        self.data = [dict()]
