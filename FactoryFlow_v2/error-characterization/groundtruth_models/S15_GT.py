"""A production line begins with a Source named SRC generating items every 2.5 seconds. 
 Every sequence of SRC is followed by a buffer ID=B_src_1.Then a line consists of 3 
 sequential stages. Each stage Stage_i Stage_1 through Stage_3 is modeled as a subsystem
containing a Machine, followed by a Buffer. Machine in each stage has a processing delay
 of 4.0,3 and2  seconds  with capacity 2,3,4 respectively. The output of Stage_3 is 
 connected to a Sink named SINK. There are 4 such sequences in parallel. 
 Name machines in stage_i as Stage_i as Stage_i_M1,, and Buffers as Stage_i_B1,for i
from 1 to 3. .. All machines have a processing_Delay of 2 and buffers have a capacity 
of 2. There is a connection between the M1 in r1 and M1 in row2 and a connection
 between M3 in row2 and M3 in row4. Name cross conecting buffer as Cross_Buffer_1, 
 Cross_Buffer_2, etc.Row index starts from 1There is a connection between the M1 in
 r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4.In every 
row and the 2nd and 3rd machines have 3 buffers in between them.And extra buffers in 
multiedge as B_2_3_1, B_2_3_2"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink





class stage(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # use unique ids that include the stage id so runtime references are unambiguous
        self.M = [Machine(env, id=f"{id}_M1", processing_delay=2.0)]
        self.add_child_node(self.M)
        self.e = [Buffer(env, id=f"{id}_B1", capacity=2)]
        self.add_child_edge(self.e)

# defining the system model

class LinearSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing source
        self.src = Source(env, id="SRC", inter_arrival_time=2.5)
        self.add_child_node(self.src)

        # initializing buffer from source to first machine
        self.B_src_1 = Buffer(env, id="B_src_1", capacity=2)
        self.add_child_edge(self.B_src_1)
        
        # initializing machines (stages)
        self.stages = [stage(env, id=f"Stage_{i+1}") for i in range(3)]
       
        self.stages[0].M[0].work_capacity = 2
        
        self.stages[1].M[0].work_capacity = 3
        
        self.stages[2].M[0].work_capacity = 4
        for stage_instance in self.stages:
            self.add_child_node(stage_instance)
        
        # initializing sink
        self.sink = Sink(env, id="SINK")
        self.add_child_node(self.sink)
        
        # connecting nodes
        # Source to first stage via its dedicated buffer
        self.B_src_1.connect(self.src, self.stages[0].M[0])
        
        self.multiedges = [Buffer(env, id=f"B_2_3_{i+1}", capacity=2) for i in range(2)]
        self.add_child_edge(self.multiedges)
        self.multiedges[0].connect(self.stages[1].M[0], self.stages[2].M[0])
        self.multiedges[1].connect(self.stages[1].M[0], self.stages[2].M[0])
        # connect each stage buffer to the next stage's machine
        for i in range(2):
            # use the explicit stage-local buffer object
            self.stages[i].e[0].connect(self.stages[i].M[0], self.stages[i+1].M[0])
        
      
        self.stages[2].e[0].connect(self.stages[2].M[0], self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        # creating 4 parallel linear sequences
        self.sequences = [LinearSequence(env, id=f"R{i+1}") for i in range(4)]
        for seq in self.sequences:
            self.add_child_node(seq)
        
        # creating cross connections
        # connection between M1 in R1 and M1 in R2
        self.cross_buffer_1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.cross_buffer_1)
        self.cross_buffer_1.connect(self.sequences[0].stages[0].M[0], self.sequences[1].stages[0].M[0])
        
        # connection between M3 in R2 and M3 in R4
        self.cross_buffer_2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.cross_buffer_2)
        self.cross_buffer_2.connect(self.sequences[1].stages[2].M[0], self.sequences[3].stages[2].M[0])

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S15_GT", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









