"""
ModelDescription:
A system with two nodes interconnected each with 3 machines in parallel. This is in parallel with another node with 2 machines in parallel. The system has 2 sources but a common_sink

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Machine, Sink, Buffer).
2. Inferred names `Source_1` and `Source_2` for the two sources, and `Common_Sink` for the sink.
3. Inferred a reusable class structure (e.g., `ParallelNode`) for the "node with machines in parallel" pattern, which will be instantiated three times: twice with 3 machines (for the first interconnected branch) and once with 2 machines (for the parallel branch).
4. Assumed the "two nodes interconnected" implies a series connection where the first node (3 machines) feeds into the second node (3 machines).
5. Assumed `Source_1` feeds the first node of the 3-machine series branch, and the second node of that branch feeds the `Common_Sink`.
6. Assumed `Source_2` feeds the single node of the 2-machine branch, which then feeds the `Common_Sink`.
7. Used `Buffer` for all edges as the default edge type.
8. Used a single buffer for every connection between components (e.g., between Source and Machines, or Machines and Machines) where the number of buffers was not specified.
9. Assumed connections involving parallel machines distribute/collect flow via buffers connected to each machine individually (e.g., Source connects to all 3 machines via 3 buffers).
10. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Reusable class for a node with machines in parallel
class ParallelNode(Node):
    def __init__(self, env, id, n=3):
        super().__init__(env, id)
        # Creating machines in parallel
        self.M = [Machine(env, id=f"M[{i}]") for i in range(n)]
        self.add_child_node(self.M)

# Main System Model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing Sources
        self.source1 = Source(env, id="Source_1")
        self.source2 = Source(env, id="Source_2")
        self.sources = [self.source1, self.source2]
        self.add_child_node(self.sources)
        
        # Initializing Common Sink
        self.sink = Sink(env, id="Common_Sink")
        self.add_child_node(self.sink)
        
        # Creating Branch 1 Nodes (3 machines each)
        self.branch1_node1 = ParallelNode(env, id="Branch1_Node1", n=3)
        self.branch1_node2 = ParallelNode(env, id="Branch1_Node2", n=3)
        
        # Creating Branch 2 Node (2 machines)
        self.branch2_node1 = ParallelNode(env, id="Branch2_Node1", n=2)
        
        self.add_child_node([self.branch1_node1, self.branch1_node2, self.branch2_node1])
        
        # Creating Edges
        self.edges = []
        edge_idx = 0
        
        # Connecting Source_1 to Branch1_Node1 (3 parallel connections)
        for i in range(3):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.source1, self.branch1_node1.M[i])
            self.edges.append(e)
            edge_idx += 1
            
        # Connecting Branch1_Node1 to Branch1_Node2 (3 parallel connections)
        for i in range(3):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.branch1_node1.M[i], self.branch1_node2.M[i])
            self.edges.append(e)
            edge_idx += 1
            
        # Connecting Branch1_Node2 to Common_Sink (3 parallel connections)
        for i in range(3):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.branch1_node2.M[i], self.sink)
            self.edges.append(e)
            edge_idx += 1
            
        # Connecting Source_2 to Branch2_Node1 (2 parallel connections)
        for i in range(2):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.source2, self.branch2_node1.M[i])
            self.edges.append(e)
            edge_idx += 1
            
        # Connecting Branch2_Node1 to Common_Sink (2 parallel connections)
        for i in range(2):
            e = Buffer(env, id=f"edge[{edge_idx}]")
            self.add_child_edge(e)
            e.connect(self.branch2_node1.M[i], self.sink)
            self.edges.append(e)
            edge_idx += 1

# Initializing SimPy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)