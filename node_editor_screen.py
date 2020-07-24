from kivy.uix.screenmanager import Screen
from skill_helper_widgets import NodeEditor
import pickle
from skill_helper_widgets import Node, Connection
import numpy as np


class NodeEditorScreen(Screen):
    def __init__(self, **kwargs):
        super(NodeEditorScreen, self).__init__(**kwargs)
        self.node_editor = None
        self.layout = None

    def on_enter(self, *args):
        super(NodeEditorScreen, self).on_enter(*args)
        if self.node_editor is None:
            self.node_editor = NodeEditor(auto_bring_to_front=False,
                                          screen_manager=self.manager)
            self.children[0].add_widget(self.node_editor, index=1)

            try:
                with open("layout.pkl", 'rb') as file:
                    self.layout = pickle.load(file)
            except(FileNotFoundError, pickle.UnpicklingError, EOFError):
                self.layout = None

            if self.layout is not None:
                for node in self.layout['nodes']:
                    self.node_editor.add_widget(Node(type=node['type'],
                                                     text=node['text'],
                                                     pos=node['pos']))
                for connection in self.layout['connections']:
                    for node in self.node_editor.children:
                        if isinstance(node, Node):
                            if tuple(node.pos) == connection['node1_pos']:
                                node1 = node
                            elif tuple(node.pos) == connection['node2_pos']:
                                node2 = node
                    c = Connection(node1, node2)
                    self.node_editor.add_widget(c, index=100)
                    c.strength = connection['strength']
                    c.direction = connection['direction']
                    node1.connections.append(c)
                    node1.connected.append(node2)
                    node2.connected.append(node1)
                    node2.connections.append(c)

    def save_layout(self):
        nodes = list()
        connections = list()
        for child in self.node_editor.children:
            if isinstance(child, Node):
                node = dict()
                node['text'] = str(child.text)
                node['pos'] = int(child.pos[0]), int(child.pos[1])
                node['type'] = str(child.type)
                nodes.append(node)
            elif isinstance(child, Connection):
                connection = dict()
                connection['node1_pos'] = int(child.node1.pos[0]), int(child.node1.pos[1])
                connection['node2_pos'] = int(child.node2.pos[0]), int(child.node2.pos[1])
                connection['strength'] = float(child.strength)
                connection['direction'] = str(child.direction)
                connections.append(connection)

        with open("layout.pkl", 'wb') as file:
            pickle.dump({'nodes': nodes, 'connections': connections}, file)

    def calculate_importance(self):
        self.size_skills = len(self.manager.database.skills)
        self.size_tasks = len(self.manager.database.tasks)
        D = np.eye(self.size_skills+self.size_tasks)
        d = np.eye(self.size_skills+self.size_tasks)

        for child in self.node_editor.children:
            if isinstance(child, Connection):
                row = self.find_item(child.node1.text, child.node1.type)
                col = self.find_item(child.node2.text, child.node2.type)
                if child.direction != 1:
                    D[row, col] = child.strength + 1
                    if child.direction == 2:
                        D[col, row] = child.strength + 1
                else:
                    D[col, row] = child.strength

        for row in range(0, D.shape[0]):
            d[row, row] = self.importance(D, row)

        # normalize
        d = d - d.min()
        d /= d.max()

        for row in range(0, self.size_skills):
            self.manager.database.skills[row]['importance'] = float(0.5*(d[row, row] + self.manager.database.skills[row]['importance']))

        for row in range(self.size_skills, D.shape[0]):
            self.manager.database.tasks[row - self.size_skills]['importance'] = float(0.5*(d[row, row] +
                                                                                     self.manager.database.tasks[row - self.size_skills]['importance']))

        self.manager.database.recalculate_priority()

    def find_item(self, name, type):
        if type == "skill":
            idx = self.manager.database.find_item(name)
        else:
            idx = self.manager.database.find_item(name) + self.size_skills
        return idx

    def importance(self, D, row):
        value = D[row, row]
        for col in range(D.shape[0]):
            if (D[row, col] != 0) and (row != col):
                # if has a feedback
                # temporarly delete this feedback
                temp = None
                if D[col, row] != 0:
                    temp = D[col, row]
                    D[col, row] = 0
                value += D[row, col] * self.importance(D, col)
                # then recover
                if temp is not None:
                    D[col, row] = temp
        return value
