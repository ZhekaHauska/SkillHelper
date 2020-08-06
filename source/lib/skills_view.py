from kivy.uix.recycleview import RecycleView


class SkillsView(RecycleView):
    def __init__(self, **kwargs):
        super(SkillsView, self).__init__(**kwargs)
        self.data = [dict()]
