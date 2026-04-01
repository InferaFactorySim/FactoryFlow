"""
ModelDescription:
A system with 2 nodes (TypeA and TypeB) interconnected. One node has 2 machines in parallel  and the second one has 2 machines in series . The output of the last in TypeB is fed back to first machine in TypeA. the system has a common source. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. Name machine IDs as M1,M2 and buffers IDs as B1, B2,.. in every node.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Created classes `TypeA` and `TypeB` to represent the repeated node structures described.
3. Assumed the "Common Source" connects to the input of Node TypeA.
4. Assumed "interconnected" implies a forward flow where the output of Node TypeA connects to the input of Node TypeB.
5. Assumed a Sink node is connected to the output of Node TypeB to allow entities to exit the system, in addition to the feedback loop.
6. In Node TypeA (Parallel), assumed the input (from  Feedback) connects to only M1 via buffer and input from Source connects to both M1 and M2 via buffers  , and the outputs of both M1 and M2 connect to Node TypeB.
7. In Node TypeB (Series), assumed M1 connects to M2 via a buffer.
8. Assumed the feedback connection flows from the output of the last machine in TypeB (M2) to the inputs of first machine in TypeA (M1 ).
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

# Node TypeA: 2 machines in parallel
class TypeA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines in parallel (M1, M2)
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        # No internal buffers required for parallel structure as connections are external

# Node TypeB: 2 machines in series
class TypeB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # Creating 2 machines in series (M1, M2)
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        # Creating internal buffer (B1)
        self.edges = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(1)]
        self.add_child_edge(self.edges)
        
        # Connecting M1 -> M2
        self.edges[0].connect(self.M[0], self.M[1])

# Overall System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing Source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # Initializing Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Initializing Node TypeA
        self.nodeA = TypeA(env, id="TypeA")
        self.add_child_node(self.nodeA)
        
        # Initializing Node TypeB
        self.nodeB = TypeB(env, id="TypeB")
        self.add_child_node(self.nodeB)
        
        # Creating buffers for system interconnections
        # B1, B2: Source -> TypeA (M1, M2)
        # B3, B4: TypeA (M1, M2) -> TypeB (M1)
        # B5: TypeB (M2) -> Sink
        # B6: TypeB (M2) -> TypeA (M1) [Feedback]
        self.edges = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(6)]
        self.add_child_edge(self.edges)
        
        # Connecting Source to TypeA (M1 and M2)
        for i in range(2):
            self.edges[i].connect(self.src, self.nodeA.M[i])
            
        # Connecting TypeA (M1 and M2) to TypeB (M1)
        for i in range(2):
            self.edges[2+i].connect(self.nodeA.M[i], self.nodeB.M[0])
            
        # Connecting TypeB (M2) to Sink
        self.edges[4].connect(self.nodeB.M[1], self.sink)
        
        # Connecting Feedback: TypeB (M2) to TypeA (M1)
        self.edges[5].connect(self.nodeB.M[1], self.nodeA.M[0])

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)