""" 
 Source_R1 feeds a logical 'Welding_Cell' via a buffer with ID B_src_R1. The cell contains Machine_W1, 
 followed by Buffer_W (cap 5).  The outputs of the cells (from Machine_W1) connects to SINK_R1. There 
 are three such cells in parallel rows R1,R2, R3 that are independent. All machines have a processing_Delay 
 of 2.

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





class WeldingCell(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # use unique ids that include the stage id so runtime references are unambiguous
        self.M = [Machine(env, id=f"Machine_W1", processing_delay=2.0)]
        self.add_child_node(self.M)
        self.e = [Buffer(env, id=f"Buffer_W", capacity=5)]
        self.add_child_edge(self.e)

# defining the system model

class LinearSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id=f"Source_{id}")
        self.add_child_node(self.src)

        # initializing buffer from source to first machine
        self.B_src = Buffer(env, id=f"B_src_{id}", capacity=5)
        self.add_child_edge(self.B_src)
        
        # initializing machines (stages)
        self.cells = [WeldingCell(env, id=f"WeldingCell_{id}") ]
       
        
        self.add_child_node(self.cells)
        
        # initializing sink
        self.sink = Sink(env, id=f"SINK_{id}")
        self.add_child_node(self.sink)
        
        # connecting nodes
        # Source to first stage via its dedicated buffer
        self.B_src.connect(self.src, self.cells[0].M[0])
        
       
        # connect each stage buffer to the next stage's machine
       
        self.cells[0].e[0].connect(self.cells[0].M[0], self.sink)
        
      
       

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # creating 4 parallel linear sequences
        self.sequences = [LinearSequence(env, id=f"R{i+1}") for i in range(3)]
        for seq in self.sequences:
            self.add_child_node(seq)
        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S16_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









