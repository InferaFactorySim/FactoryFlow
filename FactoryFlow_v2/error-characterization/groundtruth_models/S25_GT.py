"""SRC -> M1 -> M2 -> M3 -> M4 -> SINK. Inner Loop: 30% of M2 output goes back to M1. Outer Loop: 10% 
of M4 output goes back to M1. All machines delay 2, all buffers capacity 2. Name buffer IDs as 
B_srcnodeID_destinationnodeID"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

import random
def routing_gen(prob):
    while True:
        if random.random() < prob:
            yield 1
        else:
            yield 0


class Linear(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(4)]
        self.add_child_node(self.M)
        self.nodes = [self.SRC] + self.M + [self.SINK]
        ids=[(self.nodes[i].id, self.nodes[i+1].id) for i in range(len(self.nodes)-1)]
        # initializing buffers
        self.B = [Buffer(env, id=f"B_{ids[i][0]}_{ids[i][1]}", capacity=2) for i in range(len(ids))]
        self.add_child_edge(self.B)
        # connecting nodes
        for i in range(len(self.nodes)-1):
            self.B[i].connect(self.nodes[i], self.nodes[i+1])
    


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(4)]
        self.add_child_node(self.M)
        self.nodes = [self.SRC] + self.M + [self.SINK]
        ids=[(self.nodes[i].id, self.nodes[i+1].id) for i in range(len(self.nodes)-1)]
        # initializing buffers
        self.B = [Buffer(env, id=f"B_{ids[i][0]}_{ids[i][1]}", capacity=2) for i in range(len(ids))]
        self.add_child_edge(self.B)
        # connecting nodes
        for i in range(len(self.nodes)-1):
            self.B[i].connect(self.nodes[i], self.nodes[i+1])
        
        # initializing source
      
        self.B_M2_M1 = Buffer(env, id="B_M2_M1", capacity=2)
        self.add_child_edge(self.B_M2_M1)
        self.B_M4_M1 = Buffer(env, id="B_M4_M1", capacity=2)
        self.add_child_edge(self.B_M4_M1)
        # connecting rework loops
        self.B_M2_M1.connect(self.M[1], self.M[0])  # M2 to M1
        self.B_M4_M1.connect(self.M[3], self.M[0])  # M4 to M1

        self.M[1].out_edge_selection = routing_gen(0.3)  # 30% from M2 to M1
        self.M[3].out_edge_selection = routing_gen(0.1)  # 10% from M4 to M1

       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S25_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









