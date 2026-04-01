"""
ModelDescription:
A linear sequence of 8 machines with delay 2 connected with a sink and a source. There are 4 buffers between 2 and 3rd machines and 6th and 7th machine.  


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Machine IDs are inferred as M1 through M8 to represent the sequence of 8 machines and Buffer IDs are  as B1, B2,.. the extra buffers IDs as B3_1, B3_2, B3_3 and B7_1, B7_2, B7_3.
3. Source ID is inferred as "SRC" and SINK ID as "sink".
4. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
5. Flow is assumed to be linear from Source to M[0], through the sequence to M[7], and finally to Sink.
6. Used a single buffer for all connections where the number of buffers was not explicitly specified (Source to M[0], M[0] to M[1], M[2] to M[3], M[3] to M[4], M[4] to M[5], M[6] to M[7], and M[7] to Sink).
7. The specified 4 buffers are placed between M[1] (2nd machine) and M[2] (3rd machine), and between M[5] (6th machine) and M[6] (7th machine).
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
        self.source = Source(env, id="SRC")
        self.add_child_node(self.source)

        # initializing machines M1 to M8 with processing delay 2
        self.machines = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(8)]
        self.add_child_node(self.machines)

        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # initializing edges
        self.edges = []
        edge_idx = 0

        # Connecting Source to M1
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.source, self.machines[0])
        self.edges.append(e)
        edge_idx += 1

        # Connecting Machines in sequence
        for i in range(7):
            # Determine number of buffers between machines[i] and machines[i+1]
            # Between 2nd (index 1) and 3rd (index 2) -> 4 buffers
            # Between 6th (index 5) and 7th (index 6) -> 4 buffers
            num_buffers = 1
            if i == 1 or i == 5:
                num_buffers = 4
            
            for _ in range(num_buffers):
                e = Buffer(env, id=f"edge[{edge_idx}]")
                self.add_child_edge(e)
                e.connect(self.machines[i], self.machines[i+1])
                self.edges.append(e)
                edge_idx += 1

        # Connecting M8 to Sink
        e = Buffer(env, id=f"edge[{edge_idx}]")
        self.add_child_edge(e)
        e.connect(self.machines[7], self.sink)
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