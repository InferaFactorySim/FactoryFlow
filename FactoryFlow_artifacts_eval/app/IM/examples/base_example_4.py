# create a system model where 3 machines are connected in series with 2 buffers between them. Last machine is connected to 3 other machines via a buffer and finally to a sink.

# importing necessary libraries
import simpy,sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



# defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        # creating standalone n machines and adding as child nodes
        self.parallel_system = parallelMachineSystem(env, id="parallel_system", n=n)
        self.add_child_node(self.parallel_system)
       
        # creating series machine system and adding as child nodes
        self.series_system = SeriesMachineSystem(env, id="series_system", n=n)
        self.add_child_node(self.series_system)

        # creating edge between parallel system and series system
        self.e = [Buffer(env, id=f"e_series_parallel[{i}]") for i in range(n)]
        self.add_child_edge(self.e)

        self.e_sink = [Buffer(env, id=f"e_parallel_sink[{i}]") for i in range(n)]
        self.add_child_edge(self.e_sink)

        # connecting series system to parallel system using buffers
        for i in range(n):
            self.e[i].connect( self.series_system.M[-1], self.parallel_system.M[i])  

        # connecting parallel system to sink using buffers
        for i in range(n):
            self.e_sink[i].connect( self.parallel_system.M[i], self.series_system.sink)


# defining the parallel machine system( standalone machines)
class parallelMachineSystem(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        
        # creating machine and adding as child nodes
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
       
        
      

       
      
# defining the series machine system with source and with two buffers between each machine 
class SeriesMachineSystem(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)

        # creating source and adding as child nodes
        self.source = Source(env, id="src", inter_arrival_time=1.0)
        self.add_child_node(self.source)
        # creating machines and adding as child nodes
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        # creating sink and adding as child nodes
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        # Create buffer between source and first machine
        self.e_src = Buffer(env, id="e_source")
        self.add_child_edge(self.e_src)


        # Create 2 buffers between each pair of machines
        self.e = [[Buffer(env, id=f"e[{i}][{j}]") for j in range(2)] for i in range( n - 1)]
        self.add_child_edge(self.e)
   
      

        # Connect Source to M[0] with one buffer
        self.e_src.connect(self.source, self.M[0])
       

        # Connect machines with two buffers
        for i in range( n - 1):
                        
            self.e[i][0].connect(self.M[i], self.M[i + 1])
            self.e[i][1].connect(self.M[i], self.M[i + 1])

        

# initializing simpy environment
env = simpy.Environment()


# defining the top level system
TOP = SystemModel(env,"TOP") 
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()  
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)