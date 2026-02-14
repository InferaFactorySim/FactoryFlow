"""
ModelDescription:
A linear sequence of 8 machines connected with a sink and a source. There are 4 buffers between 2 and 3rd machines and 6th and 7th machine.  


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Machine IDs are inferred as M[0] through M[7] to represent the sequence of 8 machines.
3. Source ID is inferred as "src" and Sink ID as "sink".
4. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
5. Flow is assumed to be linear from Source to M[0], through the sequence to M[7], and finally to Sink.
6. Used a single buffer for all connections where the number of buffers was not explicitly specified (Source to M[0], M[0] to M[1], M[2] to M[3], M[3] to M[4], M[4] to M[5], M[6] to M[7], and M[7] to Sink).
7. The specified 4 buffers are placed between M[1] (2nd machine) and M[2] (3rd machine), and between M[5] (6th machine) and M[6] (7th machine).
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Initializing machines M[0] to M[7]
        self.M = [Machine(env, id=f"M[{i}]") for i in range(8)]
        self.add_child_node(self.M)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Defining the sequence of nodes for linear flow
        # Flow: Source -> M[0] -> ... -> M[7] -> Sink
        nodes_seq = [self.source] + self.M + [self.sink]
        
        # Creating edges and connecting nodes
        self.edges = []
        for i in range(len(nodes_seq) - 1):
            # Determine number of buffers for the connection
            # Connection 0: Source -> M[0]
            # Connection 1: M[0] -> M[1]
            # Connection 2: M[1] -> M[2] (Between 2nd and 3rd machine) -> 4 buffers
            # Connection 6: M[5] -> M[6] (Between 6th and 7th machine) -> 4 buffers
            n_buffers = 1
            if i == 2 or i == 6:
                n_buffers = 4
            
            u = nodes_seq[i]
            v = nodes_seq[i+1]
            
            if n_buffers == 1:
                edge = Buffer(env, id=f"edge[{i}]")
                self.add_child_edge(edge)
                edge.connect(u, v)
                self.edges.append(edge)
            else:
                p_edges = [Buffer(env, id=f"edge[{i}][{k}]") for k in range(n_buffers)]
                self.add_child_edge(p_edges)
                for edge in p_edges:
                    edge.connect(u, v)
                self.edges.append(p_edges)

# Initializing simpy environment
env = simpy.Environment()
# Creating the system model
TOP = SystemModel(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)