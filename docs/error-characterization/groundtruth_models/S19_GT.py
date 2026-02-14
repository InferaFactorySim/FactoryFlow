"""A source with ID Source_1(3.3s) feeds a splitter that distributes items to three parallel machines. 
Machine_Alpha has a processing delay of 1.0s. Machine_Beta and Machine_Gamma 
 have processing delays of 10.0 and 20s. All three connect to Sink_1 . All buffers 
 have a capacity of 5. Each machine has its own buffer from the source and to the sink.
 B_src_i connects Source to Machine_i, and B_sink_i connects Machine_i to Sink_1."""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink






# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id=f"Source", inter_arrival_time=3.3)
        self.add_child_node(self.src)

        # initializing buffer from source to first machine
        self.B_src = [Buffer(env, id=f"B_src_{i+1}", capacity=5) for i in range(3)]
        self.add_child_edge(self.B_src)
        
        # initializing machines (stages)
        self.machines = [
            Machine(env, id=f"Machine_Alpha", processing_delay=1.0),
            Machine(env, id=f"Machine_Beta", processing_delay=10.0),
            Machine(env, id=f"Machine_Gamma", processing_delay=20.0)
        ]
       
        
        self.add_child_node(self.machines)
        
        # initializing sink
        self.sink = Sink(env, id=f"Sink")
        self.add_child_node(self.sink)
        # initializing buffer from machines to sink
        self.B_sink = [Buffer(env, id=f"B_sink_{i+1}", capacity=5) for i in range(3)]
        self.add_child_edge(self.B_sink)
        
        # connecting nodes
        # Source to first stage via its dedicated buffer
        for i in range(3):
            self.B_src[i].connect(self.src, self.machines[i])
            self.B_sink[i].connect(self.machines[i], self.sink)
        
       
       
        
      
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S19_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









