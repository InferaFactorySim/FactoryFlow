"""
ModelDescription:
A system with 2 nodes (TypeA and TypeB) interconnected. One node has 2 machines in parallel  and the second one has 2 machines in series . The output of the last node is fed to first machine in node1. the system has a common source. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. Name machine IDs as M1,M2 and buffers IDs as B1, B2,.. in every node.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed a Sink node is added at the end of the system to terminate the flow.
3. Assumed the system topology is linear: Source -> TypeA -> TypeB -> Sink.
4. Assumed the description "output of the last node is fed to first machine in node1" refers to the connection between the first node (TypeA) and the second node (TypeB) to ensure a valid flow.
5. Assumed TypeA is the first node and TypeB is the second node.
6. Assumed TypeA consists of 2 machines (M1, M2) in parallel, where the Source connects to both M1 and M2, and both M1 and M2 connect to the first machine of TypeB.
7. Assumed TypeB consists of 2 machines (M1, M2) in series, where the input connects to M1, M1 connects to M2, and M2 connects to the Sink.
8. Assumed a single Buffer is used for every connection between components (Source-Machine, Machine-Machine, Machine-Sink).
9. Assumed Buffer IDs are generated sequentially (B1, B2...) within each node.
"""

# importing required libraries
import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src')))
from factorysimpy.utils.utils import draw_blockdiagram
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Node TypeA: 2 machines in parallel
class TypeA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # initializing machines M1, M2 with processing delay 2
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        # Parallel machines do not have internal buffers connecting them

# Node TypeB: 2 machines in series
class TypeB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # initializing machines M1, M2 with processing delay 2
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(2)]
        self.add_child_node(self.M)
        
        # initializing buffer B1 with capacity 2
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(1)]
        self.add_child_edge(self.B)
        
        # connecting M1 -> B1 -> M2
        self.B[0].connect(self.M[0], self.M[1])

# System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source with inter_arrival_time 0.3
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # initializing TypeA node
        self.type_a = TypeA(env, id="TypeA")
        self.add_child_node(self.type_a)
        
        # initializing TypeB node
        self.type_b = TypeB(env, id="TypeB")
        self.add_child_node(self.type_b)
        
        # initializing buffers for system level connections with capacity 2
        # Connections: Src->TypeA(2), TypeA(2)->TypeB(1), TypeB(1)->Sink
        # Total 5 buffers: B1..B5
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)
        
        edge_idx = 0
        
        # Connect Source to TypeA machines (Parallel)
        for i in range(2):
            self.B[edge_idx].connect(self.src, self.type_a.M[i])
            edge_idx += 1
            
        # Connect TypeA machines to TypeB first machine
        for i in range(2):
            self.B[edge_idx].connect(self.type_a.M[i], self.type_b.M[0])
            edge_idx += 1
            
        # Connect TypeB last machine to Sink
        self.B[edge_idx].connect(self.type_b.M[-1], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
fig = draw_blockdiagram(TOP)
path =fig.render(filename="factory_model_18_Detailed_V1",directory=".", format="png", cleanup=True)
TOP.validate()
# running the simulation
TOP.run_simulation(25)