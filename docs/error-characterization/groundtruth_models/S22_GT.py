"""There is a subsystem that has a source connected to 5 machines in series. This structure is repeated 
4 times, where they are in parallel, each with its own source. At the end, they are all connected to 
the common sink. The third machine in second subsystem is also connected to fourth machine in third 
subsytem and second machine in fourth subsytem with direction of edge pointing away from third machine 
in second subsystem.All machines are name as M[i], i is the position. and all buffers as B[i], i is the 
position. All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a 
interarrival time of 0.3. All machines with multiple input edges will have a work_capacity of 2"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



class LinearRow(Node):
    def __init__(self, env, id, n):
        super().__init__(env, id)
        # initializing source
        self.src = Source(env, id=f"src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        # Creating machines M[1] to M[n]
        self.M = [Machine(env, id=f"M[{i+1}]", processing_delay=2.0) for i in range(n)]
        self.add_child_node(self.M)
        
        
        # Creating buffers B[1] to B[n-1] and connecting machines in series
        
        self.B = [Buffer(env, id=f"B[{i+1}]", capacity=2) for i in range(n)]
        self.add_child_edge(self.B)

        self.B[0].connect(self.src, self.M[0])
        for i in range(n-1):
            self.B[i+1].connect(self.M[i], self.M[i+1])
        
        


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        

        self.subunits = [LinearRow(env, id=f"row{i+1}", n=5) for i in range(4)]
        self.add_child_node(self.subunits)

       
        
        # initializing machines (stages)
        self.sink = Sink(env, id=f"sink")
        self.add_child_node(self.sink)

      
        # Connecting last machine of each row to Sink
        for i in range(4):
            e = Buffer(env, id=f"B{i+1}", capacity=5)
            self.add_child_edge(e)
            e.connect(self.subunits[i].M[-1], self.sink)
       
       
        
        
        
        # Creating inter-row connections
        #row2.m3 to row3.m4
        self.B_inter1 = Buffer(env, id="B6", capacity=2)
        self.add_child_edge(self.B_inter1)
        self.B_inter1.connect(self.subunits[1].M[2], self.subunits[2].M[3])
        
        #row2.m3 to row4.m2
        self.B_inter2 = Buffer(env, id="B7", capacity=2)
        self.add_child_edge(self.B_inter2)
        self.B_inter2.connect(self.subunits[1].M[2], self.subunits[3].M[1])

       
       
        
      
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S22_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









