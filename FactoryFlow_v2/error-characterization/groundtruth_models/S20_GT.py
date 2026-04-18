"""A source with ID Source(4.32) feeds central Machine_Hub (delay 2.0s) via Buffer with 
ID- B_src_hub. Machine_Hub is connected to 5 separate output Buffers (cap 5), each 
leading to a unique Sink named Sink_North, Sink_South, Sink_East, Sink_West, and Sink_Central.
 All buffers have a capacity of 5. Each machine has its own buffer from the source and to the sink.
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
        self.src = Source(env, id=f"Source", inter_arrival_time=4.32)
        self.add_child_node(self.src)

        # initializing buffer from source to first machine
        self.B_src_hub = Buffer(env, id="B_src_hub", capacity=5)
        self.add_child_edge(self.B_src_hub)
        
        # initializing machines (stages)
        self.machine = Machine(env, id=f"Machine_Hub", processing_delay=2.0)
       
       
        
        self.add_child_node(self.machine)
        sinks_ids = ["North", "South", "East", "West", "Central"]
        self.sinks = [Sink(env, id=f"Sink_{sinks_ids[i]}") for i in range(5)]
        self.add_child_node(self.sinks)
        # initializing sink
        self.buffers_sink = [Buffer(env, id=f"B_sink_{sinks_ids[i]}", capacity=5) for i in range(5)]
        self.add_child_edge(self.buffers_sink)
        
        
        # connecting nodes
        # Source to first stage via its dedicated buffer
        self.B_src_hub.connect(self.src, self.machine)
        for i in range(5):
            
            self.buffers_sink[i].connect(self.machine, self.sinks[i])
        
       
       
        
      
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S20_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









