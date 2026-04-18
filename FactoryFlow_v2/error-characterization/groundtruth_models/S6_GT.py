"""System has 5 machines each with delay 2. 
 All machines are connected in parallel. SRC is connected to M1 and M1  
 to Sink via Buffers, B_SRC_1, B_1_SINK. 
 M2 is connected parallel to M1 using Buffer B_SRC_2 and B_2_SINK. and so on.
 All buffers have a capacity of 2.  
 System has a common source (ID= SRC) with inter arrival time of 0.2. and 
 a common sink "SINK". All machines have a processing_Delay of 1.1 """





import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


                    


class ParallelModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=1.1) for i in range(n)]
               
        self.add_child_node(self.M)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)

        
        # edges
        self.BUFFER_path=[]
        for i in range(n):
            edges=[Buffer(env, id=f"B_SRC_{i+1}", capacity=2), Buffer(env, id=f"B_{i+1}_SINK", capacity=2)]   
            self.BUFFER_path.append(edges)    
            self.add_child_edge(edges)
        # adding nodes and edges to parent node
        
        for i in range(len(self.BUFFER_path)):
            self.BUFFER_path[i][0].connect(self.SRC, self.M[i])
            self.BUFFER_path[i][1].connect(self.M[i], self.SINK)

        
        

env= simpy.Environment()
TOP = ParallelModel(env,"TOP",n=5) 

TOP.SRC.inter_arrival_time = 0.2
TOP.fill_hierarchical_id()


#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S6_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









