from kivy.uix.screenmanager import Screen
from source.lib.widgets import NodeEditor
import pickle
from source.lib.widgets import Node, Connection
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
                                                     group=node['group'],
                                                     name=node['name'],
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
                node['group'] = str(child.group)
                node['name'] = str(child.name)
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
        self.size_skills = len(self.manager.database.data['skills']['items'])
        D = np.eye(self.size_skills)
        d = np.eye(self.size_skills)

        for child in self.node_editor.children:
            if isinstance(child, Connection):
                row = self.find_item(child.node1.group, child.node1.name)
                col = self.find_item(child.node2.group, child.node2.name)
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
            self.manager.database.data['skills']['items'][row]['importance'] = float(d[row, row])

        self.manager.database.refresh_priority()
        self.manager.database.sort_items()
        self.manager.database.save()

    def find_item(self, group, name):
        for idx, x in enumerate(self.manager.database.data['skills']['items']):
            if x['group'] == group and x['name'] == name:
                return idx
        else:
            raise ValueError(f'Skill {group}/{name} is not found.')

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
