"""Subsystem_A (3 machines in series) and Subsystem_B (3 machines in series). SRC feeds both. 
A custom edge connects Subsystem_A.M2 to Subsystem_B.M3."""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



class Subsystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = Source(env, id="src")
        self.add_child_node(self.SRC)
        self.SINK = Sink(env, id="sink")
        self.add_child_node(self.SINK)
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(3)]
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
        
        # initializing source
        self.units = [Subsystem(env, id="Subsystem_A"), Subsystem(env, id="Subsystem_B")]
        self.add_child_node(self.units)

        self.B_cross_M2_M3 = Buffer(env, id="B_cross_M2_M3", capacity=2)
        self.add_child_edge(self.B_cross_M2_M3)
        self.B_cross_M2_M3.connect(self.units[0].M[1], self.units[1].M[2])
        
       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S26_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









