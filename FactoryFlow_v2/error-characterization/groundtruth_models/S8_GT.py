"""System has 8 machines each with delay 2. 
 Source (ID= SRC) with inter arrival time of 1.2. 
 All machines are interconnected via buffers. Name buffers as B1, B2, B3,.. and
   Machines as M1,M2,... All buffers have a capacity of 2. 
   The sequence ends in a sink (ID=SINK). 
   There are 4 buffers between M2 and M3 and M6 and M7. Name extra buffers as B3_1,B3_2. B7_1,B7_2
   The in_edge_selection of the machine after multiedge is "ROUND_ROBIN".  
All machines have a processing_Delay of 2 and buffers have a capacity of 2.  """


import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


                    


class LinearModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(n)]
               
        self.add_child_node(self.M)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)
        self.nodes= [self.SRC]+self.M+[self.SINK]
        
        # edges
        self.BUFFER = []
        for i in range(n+1):
            edges=Buffer(env, id=f"B{i+1}", capacity=2)  
            self.BUFFER.append(edges)    
        self.add_child_edge(self.BUFFER)
        # adding nodes and edges to parent node
        
        for i in range(len(self.BUFFER)):
            self.BUFFER[i].connect(self.nodes[i], self.nodes[i+1])

        for i in range(3):
            edge_1 = Buffer(env, id=f"B3_{i+1}", capacity=2)
            edge_2 =Buffer(env, id=f"B7_{i+1}", capacity =2)
            self.add_child_edge(edge_1)
            self.add_child_edge(edge_2)
            edge_1.connect(self.M[1], self.M[2])
            edge_2.connect(self.M[5], self.M[6])
            
        
       
            

        
        


env= simpy.Environment()
TOP = LinearModel(env,"TOP",n=8) 

TOP.SRC.inter_arrival_time = 1.2
TOP.M[2].in_edge_selection = "ROUND_ROBIN"
TOP.M[6].in_edge_selection = "ROUND_ROBIN"
TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S8_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









