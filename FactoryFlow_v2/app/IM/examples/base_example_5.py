
# system with 10 machines in series with source and sink. There are 10 such sequences and the machine in each sequence is connected to the machine in its corresponding position in the adjacent sequence using buffers.

# importing necessary libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



                        

# creating system model with multiple linear models and to interconnect sequences in parallel using buffers
class SystemModel(Node):
    def __init__(self, env, id,  machines=100, rows=100):
        
        super().__init__(env, id)
        #initializing number of machines and rows
        self.num_machines=machines
        self.num_rows=rows

        # creating multiple linear models and adding those as child nodes
        self.R = [LinearModel(env, id=f"R[{i}]", n=self.num_rows) for i in range(self.num_machines)]
        self.add_child_node(self.R)

        # creating inter connections between linear models and adding those as child edges
        self.inter_e= []
        #iterating through rows to create buffers between corresponding machines in adjacent linear models
        for i in range(self.num_rows-1):
          inter_e= [Buffer(env, id=f"inter_e[{i}][{k}]") for k in range(self.num_machines-1)]
          self.add_child_edge(inter_e)

          #iterating through machines to connect corresponding machines in adjacent linear models
          for j in range(self.num_machines-1):
            #connecting linear models in parallel using buffers
            inter_e[j].connect(self.R[i].M[j], self.R[i+1].M[j])
          self.inter_e.append(inter_e)
          
        


# defining linear model with source, multiple machines in series and sink
class LinearModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)

        # initializing source and adding as child node
        self.src = Source(env, id="src",  inter_arrival_time=0.2)
        self.add_child_node(self.src)
        # initializing machines and adding as child nodes
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)
        # initializing sink and adding as child nodes
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        
        # creating buffers to connect nodes
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n+1)]
        self.add_child_edge(self.e)
        #connecting source to machine
        self.e[0].connect(self.src, self.M[0])
        #connecting machines in series
        for i in range(n-1):
            self.e[i+1].connect(self.M[i],self.M[i+1])
        #connecting last machine to sink
        self.e[n].connect(self.M[n-1], self.sink)


        
        
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


        









