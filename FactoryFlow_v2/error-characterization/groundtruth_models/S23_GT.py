"""There is a subsystem as follows. Machine_M1 feeds Machine_M2 via a Buffer (cap 5). After Machine_M2, 
items enter Buffer_Check and Machine_check. Machine_Check routes 20% of items back to the input of 
Machine_M1 for rework and 80% forward to next machine The rework loop buffer has a capacity of 1. 
There are 3 such system.  Similarly there is another sub-system as follows- Mac_M1 acts as a router 
with a split ratio of 0.5 to Path A and 0.5 to Path B. Path A consists of Buffer_A feeding  Mac_M2. 
Path B consists of Buffer_B feeding Mac_M3. Mac_M2 and Mac_M3 both connect to individual Sinks, Sink_1 
and Sink_2 via Buffer_1 and Buffer_2 respectively. 80% out from  Machine_Check in first type of 
subsystem enters MacM1 that is in the second type of sub system. . All machines have a processing_Delay 
of 2 and buffers have a capacity of 2 unless not specified before.  The src has a interarrival time of 
0.3. All machines with multiple input edges will gave a work_capacity of 2"""

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



class subsystem1(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.src = Source(env, id=f"src", inter_arrival_time=0.3)
        self.add_child_node(self.src)

        
        # initializing machines
        self.M = [Machine(env, id=f"M{i+1}", processing_delay=2.0) for i in range(2)]
        self.add_child_node(self.M)

        self.Mcheck = Machine(env, id="Machine_check", processing_delay=2.0)
        self.add_child_node(self.Mcheck)
        
        # initializing buffers
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.B2 = Buffer(env, id="B2", capacity=5)
        self.B_check = Buffer(env, id="B_check", capacity=2)
        self.B_rework = Buffer(env, id="B_rework", capacity=1)
        self.add_child_edge([self.B1, self.B2, self.B_check, self.B_rework])
        
        # connecting nodes
        self.B1.connect(self.src, self.M[0])
        self.B2.connect(self.M[0], self.M[1])
        self.B_check.connect(self.M[1], self.Mcheck)
        self.Mcheck.out_edge_selection = routing_gen(0.8)  # 80% to forward, 20% to rework
    
class subsystem2(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing machines
        self.M = [Machine(env, id=f"Mac_M{i+1}", processing_delay=2.0) for i in range(3)]
        self.add_child_node(self.M)

        self.M[0].work_capacity = 2  # setting work capacity for router machine
        
        # initializing buffers
        self.B_A1 = Buffer(env, id="B_A1", capacity=2)
        self.B_B1 = Buffer(env, id="B_B1", capacity=2)
        self.B_A2 = Buffer(env, id="B_A2", capacity=2)
        self.B_B2 = Buffer(env, id="B_B2", capacity=2)
        self.add_child_edge([self.B_A1, self.B_B1, self.B_A2, self.B_B2])

        self.sinks = [Sink(env, id=f"sink_{i+1}") for i in range(2)]
        self.add_child_node(self.sinks)

        
        # connecting nodes
        self.B_A1.connect(self.M[0], self.M[1])
        self.B_B1.connect(self.M[0], self.M[2])
        self.B_A2.connect(self.M[1], self.sinks[0])
        self.B_B2.connect(self.M[2], self.sinks[1])


# defining the system model

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        

        self.subunits = [subsystem1(env, id=f"subsystem1_{i+1}") for i in range(3)]
        self.subunits.append(subsystem2(env, id="subsystem2"))
        self.add_child_node(self.subunits)

        
        
       

        # connecting nodes
        # Source to first stage via its dedicated buffer
        #self.subunits[0].Mcheck.out_edge_selection = routing_gen(0.8)  # 80% to subsystem2, 20% to rework
        self.b = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(3)]
        self.add_child_edge(self.b)
        for i in range(3):
           
            self.subunits[i].M[1].work_capacity = 2  # setting work capacity for Machine_Check
            self.b[i].connect(self.subunits[i].Mcheck, self.subunits[3].M[0])  # connecting Machine_Check
            self.subunits[i].B_rework.connect(self.subunits[i].Mcheck, self.subunits[i].M[0])  # connecting rework loop
        self.subunits[3].M[0].out_edge_selection = "ROUND_ROBIN"  # setting router machine selection policy
        self.subunits[3].M[0].work_capacity = 2  # setting work capacity for router machine
       
       
       
        
        
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S23_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









