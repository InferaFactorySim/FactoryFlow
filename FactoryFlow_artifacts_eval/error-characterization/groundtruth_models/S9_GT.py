"""There’s a subsytem A where a single machine is connected to 3.
machines in parallel which are then connected to another common machine. 
This subsytem is connected to another subsystem B having 2 machines in series. 
B is again connected to A. Now this whole ABA thing is repeated 3 times and is 
connected in series.Name machines as M1,M2, and Buffers as B1,B2,.. 
All machines have a processing_Delay of 2 and buffers have a capacity of 2. 
THE work_capacity of the machine following the multi-edge be 4 with in_edge_selction as "ROUND_ROBIN.
 The system has a source with ID="SRC and sink with ID=SINK"""


import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


class A(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        self.M_1 = Machine(env, id="M_1", processing_delay=2)
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(n)]
        self.M_2 = Machine(env, id="M_2", processing_delay=2, work_capacity=4, in_edge_selection="ROUND_ROBIN")   
        self.add_child_node([self.M_1]+self.M+ [self.M_2])

        
        
        # edges
        self.BUFFER_path=[]
        for i in range(3):
            edges=[Buffer(env, id=f"B_M1_{i+1}", capacity=2), Buffer(env, id=f"B_{i+1}_M2", capacity=2)]   
            self.BUFFER_path.append(edges)    
            self.add_child_edge(edges)
        # adding nodes and edges to parent node
        
        for i in range(len(self.BUFFER_path)):
            self.BUFFER_path[i][0].connect(self.M_1, self.M[i])
            self.BUFFER_path[i][1].connect(self.M[i], self.M_2)


class B(Node):
    def __init__(self, env, id, n=2):
        super().__init__(env, id)
       
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2) for i in range(n)]           
        self.add_child_node(self.M)
    
        # edges
        edges=Buffer(env, id=f"B{1}", capacity=2)  
      
        self.add_child_edge(edges)
        edges.connect(self.M[0], self.M[1])

  

class ABA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.A1= A(env, id="A1", n=3)
        self.B = B(env, id="B", n=2)
        self.A2= A(env, id="A2", n=3)
        self.add_child_node([self.A1, self.B, self.A2])



        self.edge1=Buffer(env, id=f"Binter{1}", capacity=2)  
        self.add_child_edge(self.edge1)
        self.edge1.connect(self.A1.M_2, self.B.M1)
        
        self.edge2=Buffer(env, id=f"Binter{2}", capacity=2)  
        self.add_child_edge(self.edge2)
        self.edge2.connect( self.B.M2, self.A2.M_1,)



class Linear(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.SRC = Source(env, id="SRC")
        self.add_child_node(self.SRC)
        self.clusters = [ABA(env, id=f"ABA{i}") for i in range(3)]
        self.add_child_node(self.clusters)
        self.SINK = Sink(env, id="SINK")
        self.add_child_node(self.SINK)
        self.nodes = [self.SRC]+self.clusters+[self.SINK]

        self.BUFFERS = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.BUFFERS)
        self.BUFFERS[0].connect(self.nodes[0],self.nodes[1].A1.M_1)
        self.BUFFERS[1].connect(self.nodes[1].A2.M_2,self.nodes[2].A1.M_1)
        self.BUFFERS[2].connect(self.nodes[2].A2.M_2,self.nodes[3].A1.M_1)
        self.BUFFERS[3].connect(self.nodes[3].A2.M_2,self.nodes[4])



     
            
        
       
            

        
        


env= simpy.Environment()
TOP = Linear(env,"TOP",) 

TOP.SRC.inter_arrival_time = 1.2

TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S9_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









