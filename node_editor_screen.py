from kivy.uix.screenmanager import Screen
from skill_helper_widgets import NodeEditor
import pickle
from skill_helper_widgets import Node, Connection


class NodeEditorScreen(Screen):
    def __init__(self, **kwargs):
        super(NodeEditorScreen, self).__init__(**kwargs)
        self.node_editor = None
        self.layout = None

    def on_enter(self):
        super(NodeEditorScreen, self).on_enter()
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
                    self.node_editor.add_widget(Node(text=node['text'],
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

    def save_layout(self):
        nodes = list()
        connections = list()
        for child in self.node_editor.children:
            if isinstance(child, Node):
                node = dict()
                node['text'] = str(child.text)
                node['pos'] = int(child.pos[0]), int(child.pos[1])
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


