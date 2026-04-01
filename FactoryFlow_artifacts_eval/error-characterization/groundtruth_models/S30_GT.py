""""
A production line has 4 machines ID=Main_M[i],where i=0,1,2,.. in series and a subsystem . 
The subsystem consists of 3 machines(M1,M2,M3) in series. In the production line the 
subsystem is repeated 3 times between the 2nd machine and the 4th machine. All machines 
have processing delay of 3. All buffers have ID=Bi , i =1,2,3,..

"""
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
       
 
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=3.3) for i in range(3)]
      
        self.add_child_node(self.M)
        
        # initializing buffers
        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.B)
        self.B[0].connect(self.M[0], self.M[1])
        self.B[1].connect(self.M[1], self.M[2])
        # connecting nodes

      


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        # initializing 3 instances of Cell_X with specified delays
        self.M = [Machine(env, id=f"Main_M[{i}]", processing_delay=3) for i in range(4)]
        self.cell1 = [Subsystem(env, id=f"Subsystem{i+1}") for i in range(3)]
        self.add_child_node(self.cell1)
        self.add_child_node(self.M)

        self.B = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(11)]
        self.add_child_edge(self.B)
        
        
        self.B[0].connect(self.src, self.M[0])
        self.B[1].connect(self.M[0], self.M[1])
        self.B[2].connect(self.M[1], self.M[2])
        self.B[3].connect(self.M[2], self.M[3])
        self.B[4].connect(self.M[3], self.sink)

        # connecting subsystem instances in series between Main_M[1] and Main_M[3]
        self.B[5].connect(self.M[1], self.cell1[0].M[0])
        self.B[6].connect(self.cell1[0].M[2], self.M[3])

        self.B[7].connect(self.M[1], self.cell1[1].M[0])
        self.B[8].connect(self.cell1[1].M[2], self.M[3])
        
        self.B[9].connect(self.M[1], self.cell1[2].M[0])
        self.B[10].connect(self.cell1[2].M[2], self.M[3])



        
       
        
       

        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S30_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(100)

        









