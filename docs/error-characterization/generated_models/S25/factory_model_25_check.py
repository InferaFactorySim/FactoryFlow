"""
ModelDescription:
SRC -> M1 -> M2 -> M3 -> M4 -> SINK. Inner Loop: 30% of M2 output goes back to M1. Outer Loop: 10% of M4 output goes back to M1. All machines delay 2, all buffers capacity 2. Name buffer IDs as B_srcnodeID_destinationnodeID

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Default inter-arrival time (1.0) assumed for Source 'SRC'.
3. Used 'Buffer' class for all edges with a single buffer between connected nodes.
4. M2 output routing assumed to be probabilistic: 30% to M1, remaining 70% to M3.
5. M4 output routing assumed to be probabilistic: 10% to M1, remaining 90% to SINK.
6. No repeated patterns detected, so a single SystemModel class will be used.
7. create a generator function that outputputs 1 for x% time and 2 for 1-x% time. and add that function as out_edge_selection for M2 and M4.
"""

import simpy
import random
#import factorysimpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','..','src')))
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)

        # Generator function for routing
        # Yields 0 for main path (1-x%) and 1 for feedback path (x%)
        # Using 0 and 1 to match 0-based indexing of edge lists
        def routing_gen(prob):
            while True:
                if random.random() < prob:
                    print(1)
                    yield 1
                else:
                    print(0)
                    yield 0

        # Create Source
        self.src = Source(env, id="SRC", inter_arrival_time=1.0)
        self.add_child_node(self.src)

        # Create Machines M1 to M4
        self.machines = []
        # Config: (id_suffix, routing_generator or None)
        # M2: 30% to M1 (Feedback -> Index 1)
        # M4: 10% to M1 (Feedback -> Index 1)
        machine_configs = [
            ("M1", None),
            ("M2", routing_gen(0.3)),
            ("M3", None),
            ("M4", routing_gen(0.1))
        ]

        for name, routing in machine_configs:
            kwargs = {'processing_delay': 2}
            if routing:
                kwargs['out_edge_selection'] = routing
            m = Machine(env, id=name, **kwargs)
            self.machines.append(m)
        
        self.add_child_node(self.machines)

        # Create Sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)

        # Create Edges and Connect
        # Connections list: (SourceNode, DestNode, BufferID)
        # M2 Out: Index 0 -> M3, Index 1 -> M1
        # M4 Out: Index 0 -> SINK, Index 1 -> M1
        connections = [
            (self.src, self.machines[0], "B_SRC_M1"),
            (self.machines[0], self.machines[1], "B_M1_M2"),
            (self.machines[1], self.machines[2], "B_M2_M3"),
            (self.machines[1], self.machines[0], "B_M2_M1"),
            (self.machines[2], self.machines[3], "B_M3_M4"),
            (self.machines[3], self.sink, "B_M4_SINK"),
            (self.machines[3], self.machines[0], "B_M4_M1")
        ]

        self.edges = []
        for u, v, b_id in connections:
            b = Buffer(env, id=b_id, capacity=10)
            b.connect(u, v)
            self.edges.append(b)
        
        self.add_child_edge(self.edges)

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(30)