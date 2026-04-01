"""Source_1 (rate 10s) and Source_2 (rate 10s) feed into Machine_M1 and 
Machine_M2 respectively via buffers Buffer_src1 and Buffer_src2, of capacity 2.
 M1 and M2 both output into shared Buffer_Join1 and Buffer_Join2 (capacity 10).
   Both Buffer_Joins  feeds a final Machine_M3 (delay 4.0s) which connects to Sink
   via a buffer Buffer_main_sink. All machines have a processing_Delay of 2 and buffers
     have a capacity of 2. 
The work_capacity of machine_M3 is 2."""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink





class Combiner(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = [Source(env, id=f"Source_{i+1}", inter_arrival_time=10) for i in range(2)]
        self.add_child_node(self.SRC)
        self.Machines=[Machine(env, id= f"Machine_M{i+1}", processing_delay=2) for i in range(3)]
        self.Machines[2].processing_delay = 4.0
        self.Machines[2].work_capacity = 2
        self.add_child_node(self.Machines)
        self.SINK = Sink(env, id=f"Sink")
        self.add_child_node(self.SINK)
        #self.nodes = [self.SRC]+self.Machines+self.SINK

        self.B_main_sink = Buffer(env, id="Buffer_main_sink", capacity=2)
        self.BUFFERS = [Buffer(env, id=f"Buffer_src1", capacity=2), Buffer(env, id=f"Buffer_Join1", capacity=10) ]
        self.BUFFERS += [Buffer(env, id=f"Buffer_src2", capacity=2) , Buffer(env, id=f"Buffer_Join2", capacity=10)]
        self.add_child_edge([self.B_main_sink]+self.BUFFERS)
        # adding nodes and edges to parent node
        self.BUFFERS[0].connect(self.SRC[0], self.Machines[0])
        self.BUFFERS[2].connect(self.SRC[1], self.Machines[1])
        self.BUFFERS[1].connect(self.Machines[0], self.Machines[2])
        self.BUFFERS[3].connect(self.Machines[1], self.Machines[2])
        self.B_main_sink.connect( self.Machines[2], self.SINK)



     
            
        
       
            

        
        


env= simpy.Environment()
TOP = Combiner(env,"TOP",) 

TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S11_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









