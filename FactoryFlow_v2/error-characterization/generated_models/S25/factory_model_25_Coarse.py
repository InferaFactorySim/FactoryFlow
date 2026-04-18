"""
ModelDescription:
A system with 4 machines in series.An output of M2 output goes back to M1. An output of M4 output goes back to M1. .

 MODEL ASSUMPTIONS:
1. Node names (M1, M2, M4) are chosen according to the user's description, and M3 is inferred to complete the set of 4 machines.
2. Added a Source node ('src') to feed the first machine (M1) and a Sink node ('sink') to receive output from the last machine (M4) to complete the system flow.
3. Used 'Buffer' as the default edge type for all connections.
4. Used a single buffer for every connection between nodes.
5. Inferred a linear forward flow sequence: Source -> M1 -> M2 -> M3 -> M4 -> Sink.
6. Inferred feedback connections M2 -> M1 and M4 -> M1 as specified.
7. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
8. Assumed standard routing logic for machines with multiple outputs (M2 and M4) as no specific split ratios were provided.
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
        
        # Creating nodes
        
        # Initializing source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing 4 machines in series (M1 to M4)
        self.M = [Machine(env, id=f"M[{i}]") for i in range(4)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        # We need:
        # 1 edge from Source to M1
        # 3 edges between machines (M1->M2, M2->M3, M3->M4)
        # 1 edge from M4 to Sink
        # 1 feedback edge from M2 to M1
        # 1 feedback edge from M4 to M1
        # Total = 1 + 3 + 1 + 1 + 1 = 7 edges
        self.edges = [Buffer(env, id=f"edge[{i}]") for i in range(7)]
        self.add_child_edge(self.edges)
        
        # Connecting nodes with edges
        
        # Source to M1 (M[0])
        self.edges[0].connect(self.src, self.M[0])
        
        # Connecting machines in series: M1->M2, M2->M3, M3->M4
        for i in range(3):
            self.edges[i+1].connect(self.M[i], self.M[i+1])
            
        # M4 (M[3]) to Sink
        self.edges[4].connect(self.M[3], self.sink)
        
        # Feedback: M2 (M[1]) to M1 (M[0])
        self.edges[5].connect(self.M[1], self.M[0])
        
        # Feedback: M4 (M[3]) to M1 (M[0])
        self.edges[6].connect(self.M[3], self.M[0])

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation for 25 time units
TOP.run_simulation(25)