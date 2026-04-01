"""SRC(0.3)-M1-M2-Sink. one output of M2 goes back to M1 also. 
All connections are via single buffers. Name buffers B1, B2,..  
All machines have a processing_Delay of 2 and buffers have a capacity of 2. """


import simpy
import factorysimpy
# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

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
        self.SINK = Sink(env, id="Sink")
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
        
        self.buffer_loop=Buffer(env, id=f"B4", capacity=2)
        self.add_child_edge(self.buffer_loop)
        self.buffer_loop.connect(self.M[1], self.M[0])
            

        
        

env= simpy.Environment()
TOP = LinearModel(env,"TOP",n=2) 

TOP.SRC.inter_arrival_time = 0.3




TOP.fill_hierarchical_id()
# from factorysimpy.utils import utils
# fig = utils.draw_blockdiagram(TOP)
# path = fig.render(filename="S4_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









