
# A system with 3 linear models each having 4 machines connected by buffers with a source and sink.


# importing required libraries

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


# defining the parent node with all the 3 linear models as child nodes
class SystemModel(Node):
    def __init__(self, env, id, num_seq=2):
        super().__init__(env, id)

        # creating 3 linear models and adding those as child nodes. Each with 4 machines
        self.R = [LinearModel(env, id=f"R[{i}]",n= 4) for i in range(num_seq)]
        self.add_child_node(self.R)
        




# defining the model
# linear model with n machines
class LinearModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        # creating nodes

        # initializing source
        self.src = Source(env, id="src")
        # adding source to child nodes
        self.add_child_node(self.src)
       
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        # adding machines to child nodes
        self.add_child_node(self.M)
       
        # initializing sink
        self.sink = Sink(env, id="sink")
        # adding sink to child nodes
        self.add_child_node(self.sink)

        
        # creating edges
        # initializing buffers
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        # adding edges to child edges
        self.add_child_edge(self.e)
    
        # connecting nodes with edges
        #src to first machine
        self.e[0].connect(self.src, self.M[0])
        # machines in between
        for i in range(n-1):
            self.e[i+1].connect(self.M[i],self.M[i+1])
        # last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)


        
        
# initiliating simpy environment
env= simpy.Environment()
# creating parallel model with 3 linear sequences
TOP = SystemModel(env,"TOP", num_seq=3) 
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# simulation for 25 time units
TOP.run_simulation(25)



        









