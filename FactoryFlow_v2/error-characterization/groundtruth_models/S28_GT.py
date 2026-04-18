""""A hierarchical subsystem Cell_X consists of two machines in series with a buffer in between. 
Three instances of Cell_X are connected in series:
Cell_X_1 has delays (2.0, 2.0)
Cell_X_2 has delays (2.5, 2.0)
Cell_X_3 has delays (3.0, 2.5)
Name machines as M1,M2,.. and buffers as B1,B2,..
All buffers have capacity 2.Single Source(2.1) and Sink."""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


class Cell_X(Node):
    def __init__(self, env, id, d1, d2):
        super().__init__(env, id)
       
 
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.M[0].processing_delay = d1
        self.M[1].processing_delay = d2
        self.add_child_node(self.M)
        
        # initializing buffers
        self.B = Buffer(env, id=f"B1", capacity=2)
        self.add_child_edge(self.B)
        # connecting nodes
    
        self.B.connect(self.M[0], self.M[1])  
    


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.src = Source(env, id="src", inter_arrival_time=2.1)
        self.add_child_node(self.src)
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        # initializing 3 instances of Cell_X with specified delays
        self.cell1 = Cell_X(env, id="Cell_X_1", d1=2.0, d2=2.0)
        self.cell2 = Cell_X(env, id="Cell_X_2", d1=2.5, d2=2.0)
        self.cell3 = Cell_X(env, id="Cell_X_3", d1=3.0, d2=2.5)
        self.add_child_node([self.cell1, self.cell2, self.cell3])

        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.B)
        
        
        self.B[0].connect(self.src, self.cell1.M[0])
        self.B[1].connect(self.cell1.M[1], self.cell2.M[0])
        self.B[2].connect(self.cell2.M[1], self.cell3.M[0])
        self.B[3].connect(self.cell3.M[1], self.sink)
        
       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S28_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









