""""Source "SRC" feeds Cell_Top, which contains- Machine_T1, a Subsystem Cell_Sub, which itself contains 
two parallel machines feeding a machine and finally a Machine_T2.Buffer IDs are all B1, B2,.. 
(capacity=2) connect all elements.Final output goes to "SINK". All machines are with delay 3.3 """

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


class Cell_Sub(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
       
 
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=3.3) for i in range(3)]
      
        self.add_child_node(self.M)
        
        # initializing buffers
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.B)
        self.B[0].connect(self.M[0], self.M[2])
        self.B[1].connect(self.M[1], self.M[2])
        # connecting nodes
class Cell_Top(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
       
 
        # initializing machines
        self.M = [Machine(env, id=f"Machine_T{i+1}", processing_delay=3.3) for i in range(2)]
        self.cell_sub = Cell_Sub(env, id="Cell_Sub")
        self.add_child_node([self.cell_sub] + self.M)
    
        
        # initializing buffers
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(3)]
        self.add_child_edge(self.B)
        # connecting nodes
        self.B[0].connect(self.M[0], self.cell_sub.M[0])
        self.B[1].connect(self.M[0], self.cell_sub.M[1])
        self.B[2].connect(self.cell_sub.M[2], self.M[1])
      


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.src = Source(env, id="SRC")
        self.add_child_node(self.src)
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        # initializing 3 instances of Cell_X with specified delays
        self.cell1 = Cell_Top(env, id="Cell_Top")
        self.add_child_node(self.cell1)

        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.B)
        
        
        self.B[0].connect(self.src, self.cell1.M[0])
        self.B[1].connect(self.cell1.M[1], self.sink)
        
       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S29_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









