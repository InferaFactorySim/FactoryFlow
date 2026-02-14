"""
ModelDescription:
A linear sequence of 3 machines each with a delay of 4,3,2 connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. 

 MODEL ASSUMPTIONS:
1. A class named `LinearSequence` is created to represent the repeated pattern of "A linear sequence of 3 machines... connected with a sink and a source".
2. The system consists of 4 instances of `LinearSequence`, named `Row[0]` through `Row[3]`.
3. Inside each sequence, the machines are named `M[0]`, `M[1]`, and `M[2]`. The processing delays 4, 3, and 2 are assigned to `M[0]`, `M[1]`, and `M[2]` respectively.
4. Each `LinearSequence` contains its own local `Source` and `Sink` (rather than a common global source/sink).
5. `Buffer` edges are used for all connections, with a single buffer placed between any pair of connected nodes.
6. The connection "between M1 in r1 and M1 in row2" is assumed to be a directed flow from `Row[0].M[0]` to `Row[1].M[0]`.
7. The connection "between M3 in row2 and M3 in row4" is assumed to be a directed flow from `Row[1].M[2]` to `Row[3].M[2]`.
8. Used default values for all missing parameters (e.g., source inter-arrival times, buffer capacities) for all components.
"""

import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the repeated linear sequence model
class LinearSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # initializing machines with specific delays
        delays = [4, 3, 2]
        self.M = []
        for i in range(3):
            m = Machine(env, id=f"M[{i}]", processing_delay=delays[i])
            self.M.append(m)
        self.add_child_node(self.M)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # creating edges
        # 4 edges: src->M0, M0->M1, M1->M2, M2->sink
        self.e = [Buffer(env, id=f"edge[{i}]") for i in range(4)]
        self.add_child_edge(self.e)
        
        # connecting nodes
        self.e[0].connect(self.source, self.M[0])
        for i in range(2):
            self.e[i+1].connect(self.M[i], self.M[i+1])
        self.e[3].connect(self.M[2], self.sink)

# defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # creating 4 instances of LinearSequence
        self.rows = [LinearSequence(env, id=f"Row[{i}]") for i in range(4)]
        self.add_child_node(self.rows)
        
        # creating cross connection edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(2)]
        self.add_child_edge(self.edges)
        
        # connecting M1 in r1 (Row[0].M[0]) to M1 in row2 (Row[1].M[0])
        self.edges[0].connect(self.rows[0].M[0], self.rows[1].M[0])
        
        # connecting M3 in row2 (Row[1].M[2]) to M3 in row4 (Row[3].M[2])
        self.edges[1].connect(self.rows[1].M[2], self.rows[3].M[2])

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)