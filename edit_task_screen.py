from kivy.uix.button import Button


class SaveTaskButton(Button):
    def edit_item(self):
        task_data = {"name": self.item_name.text,
                      "description": self.item_description.text,
                      "time": float(self.item_time.text),
                      "importance": float(self.item_importance)}

        self.screen_manager.db_tasks.edit_item(task_data, self.edit_screen.curr_item['item_id'])
        self.screen_manager.current = 'tasks_screen'