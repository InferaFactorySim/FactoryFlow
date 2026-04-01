"""A system with 2 nodes (TypeA and TypeB) interconnected. One node has 2 machines in parallel  and the 
second one has 2 machines in series . The output of the last in TypeB is fed back to first machine in 
TypeA. the system has a common source. All machines have a processing_Delay of 2 and buffers have a 
capacity of 2.  The src has a interarrival time of 0.3. Name machine IDs as M1,M2 and buffers IDs as 
B1, B2,.. in every node.
"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink





class TypeA(Node):
    def __init__(self, env, id, num_machines):
        super().__init__(env, id)
        # use unique ids that include the stage id so runtime references are unambiguous
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(num_machines)]
        self.add_child_node(self.M)

class TypeB(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # use unique ids that include the stage id so runtime references are unambiguous
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(2)]
        self.add_child_node(self.M)
       
        # Creating buffer between M1 and M2
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(1)]
        self.add_child_edge(self.B)
        
        # Connecting M1 to M2
        self.B[0].connect(self.M[0], self.M[1])
       

# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id=f"src", inter_arrival_time=.3) 
        self.add_child_node(self.src)
        
        # initializing nodes
        self.nodeA = TypeA(env, id="TypeA", num_machines=2)
        self.add_child_node(self.nodeA)
        self.nodeB = TypeB(env, id="TypeB")
        self.add_child_node(self.nodeB)

        # initializing sink
        self.sink = Sink(env, id=f"sink")
        self.add_child_node(self.sink)
        # creating buffers for system interconnections
        # B1, B2: Source -> TypeA (M1, M2)  
        # B3, B4: TypeA (M1, M2) -> TypeB (M1)
        # B5: TypeB (M2) -> Sink
        
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(5)]
        self.add_child_edge(self.B)
        
        # Connecting Source to TypeA machines
        self.B[0].connect(self.src, self.nodeA.M[0])
        self.B[1].connect(self.src, self.nodeA.M[1])
        
        # Connecting TypeA machines to TypeB machine M1
        self.B[2].connect(self.nodeA.M[0], self.nodeB.M[0])
        self.B[3].connect(self.nodeA.M[1], self.nodeB.M[0])
        
        # Connecting TypeB machine M2 to Sink
        self.B[4].connect(self.nodeB.M[1], self.sink)
        
        # Feedback connection: TypeB machine M2 to TypeA machine M1
        self.B_feedback = Buffer(env, id="B6", capacity=2)
        self.add_child_edge(self.B_feedback)
        self.B_feedback.connect(self.nodeB.M[1], self.nodeA.M[0])

        
        
      
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S18_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









