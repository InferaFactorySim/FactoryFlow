"""A node named parallel_mac_3 has 3 machines in parallel.
2 such nodes are interconnected in a series and this is in parallel with a node
 named parallel_mac_2 which has 2 machines in parallel. The system has 2 sources 
 but a common_sink. Name machine s M1,M2 and buffers as B1, B2,.. source as Src_1 
 and Src_2. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  
The sources have a interarrival time of 0.5"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink





class Parallel_mac_n(Node):
    def __init__(self, env, id, num_machines):
        super().__init__(env, id)
        # use unique ids that include the stage id so runtime references are unambiguous
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(num_machines)]
        self.add_child_node(self.M)
       

# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = [Source(env, id=f"Src_{i+1}", inter_arrival_time=.5) for i in range(2)]
        self.add_child_node(self.src)

        # initializing buffer from source to first machine
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(13)]
        self.add_child_edge(self.B)
        
        # initializing machines (stages)
        self.subunits = [Parallel_mac_n(env, id="parallel_mac_3_1", num_machines=3),
                         Parallel_mac_n(env, id="parallel_mac_3_2", num_machines=3),
                         Parallel_mac_n(env, id="parallel_mac_2", num_machines=2)]
       
        
        self.add_child_node(self.subunits)

        # initializing sink
        self.sink = Sink(env, id=f"SINK")
        self.add_child_node(self.sink)
        
        # src- parallel_mac_3_1- parallel_mac_3_2 - sink
        self.B[0].connect(self.src[0], self.subunits[0].M[0])
        self.B[1].connect(self.src[0], self.subunits[0].M[1])
        self.B[2].connect(self.src[0], self.subunits[0].M[2])
        self.B[3].connect(self.subunits[0].M[0], self.subunits[1].M[0])
        self.B[4].connect(self.subunits[0].M[1], self.subunits[1].M[1])
        self.B[5].connect(self.subunits[0].M[2], self.subunits[1].M[2])
        self.B[6].connect(self.subunits[1].M[0], self.sink)
        self.B[7].connect(self.subunits[1].M[1], self.sink)
        self.B[8].connect(self.subunits[1].M[2], self.sink)

        # src- parallel_mac_2 - sink
        self.B[9].connect(self.src[1], self.subunits[2].M[0])
        self.B[10].connect(self.src[1], self.subunits[2].M[1])
        self.B[11].connect(self.subunits[2].M[0], self.sink)
        self.B[12].connect(self.subunits[2].M[1], self.sink)

        
        
        
      
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S17_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









