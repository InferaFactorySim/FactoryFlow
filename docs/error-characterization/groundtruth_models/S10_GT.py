"""Source_1 (arrival rate 5.0s) feeds Machine_M1 via Buffer with ID- buffer_main. 
M1 acts as a router with a split ratio of 0.5 to Path A and 0.5 to Path B. Path A 
consists of Buffer with ID-Buffer_A_1 feeding Machine_M2 and Buffer with 
ID-Buffer_A_sink to Sink_1. Path B consists of Buffer with ID- Buffer_B_1 
feeding Machine_M3 to Buffer with ID- Buffer_B_sink to Sink_2. M2 and M3 both connect 
to individual Sinks, Sink_1 and Sink_2 via Buffer with ID- Buffer_A_sink and Buffer 
with ID- Buffer_B_sink respectively. The out_edge_selection of Machine_M1 is "ROUND_ROBIN".
All machines have a processing_Delay of 2 and buffers have a capacity of 2"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink





class Splitter(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = Source(env, id="Source_1")
        self.add_child_node(self.SRC)
        self.Machines=[Machine(env, id= f"Machine_M{i+1}", processing_delay=2) for i in range(3)]
        self.add_child_node(self.Machines)
        self.SINK = [Sink(env, id=f"Sink_{i+1}") for i in range(2)]
        self.add_child_node(self.SINK)
        #self.nodes = [self.SRC]+self.Machines+self.SINK

        self.B_src_main = Buffer(env, id="buffer_main", capacity=2)
        self.BUFFERS = [Buffer(env, id=f"Buffer_A_1", capacity=2) , Buffer(env, id=f"Buffer_A_sink", capacity=2),]
        self.BUFFERS += [Buffer(env, id=f"Buffer_B_1", capacity=2) , Buffer(env, id=f"Buffer_B_sink", capacity=2),]
        self.add_child_edge([self.B_src_main]+self.BUFFERS)
        # adding nodes and edges to parent node
        self.B_src_main.connect(self.SRC, self.Machines[0])
        self.BUFFERS[0].connect(self.Machines[0], self.Machines[1])
        self.BUFFERS[1].connect(self.Machines[1], self.SINK[0])
        self.BUFFERS[2].connect(self.Machines[0], self.Machines[2])
        self.BUFFERS[3].connect(self.Machines[2], self.SINK[1])



     
            
        
       
            

        
        


env= simpy.Environment()
TOP = Splitter(env,"TOP",) 

TOP.SRC.inter_arrival_time = 1.2

TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S10_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









