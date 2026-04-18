"""
ModelDescription:
A series with 2 machines. There is a feedback loop that uses multiple parallel buffers for the return path from M2 to M1.

 MODEL ASSUMPTIONS:
1. Inferred the presence of a Source node named 'src' connected to M1 and a Sink node named 'sink' connected to M2 to complete the manufacturing flow.
2. Assumed the machine identifiers are 'M1' and 'M2' based on the feedback path description.
3. Assumed the "multiple parallel buffers" in the feedback loop consists of exactly 2 buffers connecting M2 back to M1.
4. Used default edge type 'Buffer' for all connections (Source to M1, M1 to M2, M2 to Sink, and feedback paths) as edge types were not specified.
5. Assumed single buffers are used for the forward connections (Source to M1, M1 to M2, M2 to Sink).
6. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)

        # initializing machines M1 and M2
        self.machines = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.machines)

        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # creating edges
        self.edges = []
        edge_idx = 0

        # Connect Source to M1
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.source, self.machines[0])
        self.edges.append(e)
        edge_idx += 1

        # Connect M1 to M2
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.machines[0], self.machines[1])
        self.edges.append(e)
        edge_idx += 1

        # Connect M2 to Sink
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.machines[1], self.sink)
        self.edges.append(e)
        edge_idx += 1

        # Feedback loop: M2 to M1 with 2 parallel buffers
        for i in range(2):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.machines[1], self.machines[0])
            self.edges.append(e)
            edge_idx += 1

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)