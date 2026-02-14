"""System has 5 machines (M1-M5) in series.
 M1(delay 1.0, cap 1), M2(2.0, 2), M3(0.5, 5), M4(3.0, 1), M5(1.5, 3). 
 SRC (rate 1.0) feeds M1 via B1. 
All inter-machine buffers have capacity 2. Ends in SINK.. """


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
        self.M = [Machine(env, id=f"M{i+1}") for i in range(n)]
               
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
        
       
            

        
        


env= simpy.Environment()
TOP = LinearModel(env,"TOP",n=5) 
params = [(1.0,1),(2.0,2),(0.5,5),(3.0,1),(1.5,3)]
for i in range(len(TOP.M)):
    TOP.M[i].processing_delay = params[i][0]
    TOP.M[i].work_capacity = params[i][1]
TOP.SRC.inter_arrival_time = 1
TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S7_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









