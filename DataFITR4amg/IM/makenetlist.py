import networkx as nx
import numpy as np

def preprocess_components(components_list):
    """
    Update 'inp' and 'out' connections in the components list.
    If 'inp' is None, it is updated to f"None_{nodename}_inp".
    If 'out' is None, it is updated to f"None_{nodename}_out".
    """
    for component in components_list:
        node_id = component['id']

        # Process 'inp' connections
        if component.get('inp') is None or component['inp'] == "None":
            component['inp'] = f"None_{node_id}_inp"

        # Process 'out' connections
        if component.get('out') is None or component['out'] == "None":
            component['out'] = f"None_{node_id}_out"

    return components_list

class Netlist:
    def __init__(self):
        self.components = []
        self.connections = []
        self.graph = nx.DiGraph()
        self.component_dict = {}

    def initialize_components(self, components_list):
        # Add real components first
        components_list = preprocess_components(components_list)
        # First, add all components
        for component_dict in components_list:
            component = {
                "id": component_dict['id'],
                "type": component_dict['type'],
                "params": {k: v for k, v in component_dict.items()
                            if k not in ['id', 'type', 'inp', 'out']},
                "inp": component_dict.get('inp'),
                "out": component_dict.get('out')
            }
            self._add_component(component)

        # Process connections and add placeholder components
        for component_dict in components_list:
            current_id = component_dict['id']

            # Process inputs (sources to current component)
            if component_dict.get('inp'):
                for source in component_dict['inp'].split():
                    self._add_placeholder_component(source, "inp")
                    self.add_connection({"source": source, "target": current_id})

            # Process outputs (current component to targets)
            if component_dict.get('out'):
                for target in component_dict['out'].split():
                    self._add_placeholder_component(target, "out")
                    self.add_connection({"source": current_id, "target": target})

        return self.component_dict

    def _add_placeholder_component(self, node_id, direction):
        """Create special source/sink components for placeholders, including edges."""
        if node_id.startswith("None_"):
            if node_id not in self.component_dict:
                placeholder_type = "Source" if "_inp" in node_id else "Sink"
                component = {
                    "id": node_id,
                    "type": placeholder_type,
                    "params": {},
                    "inp": None,
                    "out": None
                }
                self._add_component(component)
        elif "Conveyor" in node_id or "Buffer" in node_id or "Transporter" in node_id:
            # Edges are treated as nodes in the graph
            if node_id not in self.component_dict:
                component = {
                    "id": node_id,
                    "type": "Edge",
                    "params": {},
                    "inp": f"None_{node_id}_inp",
                    "out": f"None_{node_id}_out"
                }
                self._add_component(component)
                self.add_connection({"source": component['inp'], "target": node_id})
                self.add_connection({"source": node_id, "target": component['out']})

    def _add_component(self, component):
        """Helper to add components to all tracking structures"""
        self.components.append(component)
        self.component_dict[component['id']] = component
        self.graph.add_node(component['id'], **component)

    def add_connection(self, connection_dict):
        connection = {
            "source": connection_dict['source'],
            "target": connection_dict['target']
        }
        if connection not in self.connections:
            self.connections.append(connection)
            self.graph.add_edge(connection['source'], connection['target'])
        return connection

    def make_list(self):
        """
        Returns a linearized list of component IDs using topological sort.
        Only includes real components (ignores None_ placeholders if needed).
        """
        try:
            # You may want to exclude placeholder nodes if not required
            sorted_nodes = list(nx.topological_sort(self.graph))
            # Optional: filter out placeholder nodes
            filtered_nodes = [n for n in sorted_nodes if not n.startswith("None_")]
            return filtered_nodes
        except nx.NetworkXUnfeasible:
            print("Cycle detected: topological sort not possible.")
            return []