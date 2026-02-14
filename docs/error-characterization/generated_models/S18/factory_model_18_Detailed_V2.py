"""
ModelDescription:
A system with 2 nodes (TypeA and TypeB) interconnected. One node has 2 machines in parallel  and the second one has 2 machines in series . The output of the last in TypeB is fed back to first machine in TypeA. the system has a common source. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. Name machine IDs as M1,M2 and buffers IDs as B1, B2,.. in every node.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Created classes `TypeA` and `TypeB` to represent the repeated node structures described.
3. Assumed the "Common Source" connects to the input of Node TypeA.
4. Assumed "interconnected" implies a forward flow where the output of Node TypeA connects to the input of Node TypeB.
5. Assumed a Sink node is connected to the output of Node TypeB to allow entities to exit the system, in addition to the feedback loop.
6. In Node TypeA (Parallel), assumed the input (from Source and Feedback) connects to both M1 and M2 via buffers, and the outputs of both M1 and M2 connect to Node TypeB.
7. In Node TypeB (Series), assumed M1 connects to M2 via a buffer.
8. Assumed the feedback connection flows from the output of the last machine in TypeB (M2) to the inputs of both machines in TypeA (M1 and M2).
9. Used a single Buffer for all connections between machines and nodes where not explicitly specified.
10. Assumed sequential naming for buffers (B1, B2, etc.) within each node starting from the input edges.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Class TypeA: 2 machines in parallel
class TypeA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines in parallel
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)

# Class TypeB: 2 machines in series
class TypeB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        # Creating buffer between M1 and M2
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(1)]
        self.add_child_edge(self.B)
        
        # Connecting M1 to M2
        self.B[0].connect(self.M[0], self.M[1])

# System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.source)
        
        # Initializing TypeA node
        self.type_a = TypeA(env, id="TypeA")
        self.add_child_node(self.type_a)
        
        # Initializing TypeB node
        self.type_b = TypeB(env, id="TypeB")
        self.add_child_node(self.type_b)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating edges
        self.e = []
        edge_idx = 0
        
        # Connecting Source to TypeA machines (M1, M2)
        for m in self.type_a.M:
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.source, m)
            self.e.append(buf)
            edge_idx += 1
            
        # Connecting TypeA machines (M1, M2) to TypeB first machine (M1)
        for m in self.type_a.M:
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(m, self.type_b.M[0])
            self.e.append(buf)
            edge_idx += 1
            
        # Connecting TypeB last machine (M2) to Sink
        buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
        self.add_child_edge(buf)
        buf.connect(self.type_b.M[-1], self.sink)
        self.e.append(buf)
        edge_idx += 1
        
        # Feedback: Connecting TypeB last machine (M2) to TypeA machines (M1, M2)
        for m in self.type_a.M:
            buf = Buffer(env, id=f"edge[{edge_idx}]", capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.type_b.M[-1], m)
            self.e.append(buf)
            edge_idx += 1

# Initializing simpy environment
env = simpy.Environment()
# Creating system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)