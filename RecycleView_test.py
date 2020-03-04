from kivy.app import App
from kivy.lang import Builder
from kivy.uix.recycleview import RecycleView

Builder.load_file("skills_view.kv")
Builder.load_file("skill_helper_widgets.kv")


class TestApp(App):
    def build(self):
        return SkillsView()


if __name__ == '__main__':
    TestApp().run()
