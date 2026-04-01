"""M1 feeds M2. M2 feeds SINK. A return path exists from M2 back to M1, but it consists of 3 parallel 
buffers (B_ret1, B_ret2, B_ret3). M2 uses "ROUND_ROBIN" to distribute the feedback items across these 
3 buffers."""

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
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}") for i in range(2)]
        self.add_child_node(self.M)
        self.nodes = [self.SRC] + self.M + [self.SINK]
        ids=[(self.nodes[i].id, self.nodes[i+1].id) for i in range(len(self.nodes)-1)]
        # initializing buffers
        self.B = [Buffer(env, id=f"B_{ids[i][0]}_{ids[i][1]}") for i in range(len(ids))]
        self.add_child_edge(self.B)
        # connecting nodes
        for i in range(len(self.nodes)-1):
            self.B[i].connect(self.nodes[i], self.nodes[i+1])
    
        
        
        self.B_ret = [Buffer(env, id=f"B_ret{i+1}") for i in range(3)]
        self.add_child_edge(self.B_ret)
        # connecting feedback buffers from M2 to M1
        for i in range(3):
            self.B_ret[i].connect(self.nodes[2], self.nodes[1])
        self.nodes[2].out_edge_selection="ROUND_ROBIN"
        
       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S27_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









