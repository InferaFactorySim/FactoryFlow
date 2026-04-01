
# A linear sequence of 4 machines are connected by buffers. Between 2nd and 3rd machine there are 2 buffers. 3 such linear models are connected in parallel to form the system and the system has a common source and a common sink.

# importing necessary libraries
import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink



# defining the overall system model                        
class SystemModel(Node):
    
    def __init__(self, env, id, clusters=3):
        super().__init__(env, id)
        self.num_clusters=clusters

        # creating source and adding as child nodes
        self.src= Source(env, id="src")
        self.add_child_node(self.src)
        
        # creating sink and adding as child nodes
        self.sink= Sink(env, id="sink")
        self.add_child_node(self.sink)



        # creating clusters and adding those as child nodes
        self.clusters=[cluster(env, id=f"cluster[{i}]") for i in range(self.num_clusters)]
        self.add_child_node(self.clusters)
        
        #creating edges between source and first machine in all cluster
        self.source_edges= [Buffer(env, id=f"source_edges[{j}]") for j in range(self.num_clusters)]
        self.add_child_edge(self.source_edges)

        # connecting source to first machine in all clusters using buffers
        for j in range(self.num_clusters):
            self.source_edges[j].connect( self.src, self.clusters[j].cluster_blocks[0].M[0])
        
        
        # creating edges between last machine in all clusters and sink
        self.sink_edges= [Buffer(env, id=f"sink_edges[{j}]") for j in range(self.num_clusters)]
        self.add_child_edge(self.sink_edges)
        # connecting last machine in all clusters to sink using buffers
        for j in range(self.num_clusters):
            self.sink_edges[j].connect( self.clusters[j].cluster_blocks[-1].M[1], self.sink)

# defining the cluster model. A cluster has 2 linear models connected in series with 2 buffers         
class cluster(Node):
    
    def __init__(self, env, id, n=5 ):
        super().__init__(env, id)

        # creating 2 linear models and adding those as child nodes. Each with 2 machines
        self.cluster_blocks=[LinearModel(env, id=f"R[{i}]",n=2) for i in range(2)]
        self.add_child_node(self.cluster_blocks)
       
        self.cluster_edges= [Buffer(env, id=f"cluster_edges[{j}]") for j in range(2)]
        self.add_child_edge(self.cluster_edges)
        # connecting the linear models in parallel using buffers
        for j in range(2):
            self.cluster_edges[j].connect( self.cluster_blocks[0].M[1], self.cluster_blocks[1].M[0])
        



# defining the model
# linear model with n machines without a source and sink
class LinearModel(Node):
    def __init__(self, env, id, n=5):
        super().__init__(env, id)
        # creating nodes       
        # initializing machines
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        # adding machines to child nodes
        self.add_child_node(self.M)  
        # creating edges
        # initializing buffers
        self.e = [Buffer(env, id=f"e[{i}]") for i in range(n-1)]
        # adding edges to child edges
        self.add_child_edge(self.e)
        # connecting nodes with edges
        # machines in between
        for i in range(n-1):
            self.e[i].connect(self.M[i],self.M[i+1])
       

        
        
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


        









