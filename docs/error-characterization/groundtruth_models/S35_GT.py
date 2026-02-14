"""
ModelDescription:
A systemA with  machine (Mp_in)  that splits into 10 machines  and the output from these 
machines ends in another a machine  (Mp_out) . There are 5 such systems that are connected 
in series .  There is another systemB with 10 machines in series and there are 5 such systems. 
The last machine in systemA is connected to the first machines in each row in systemB. 
Machines in parallel systems will have ID Mp[i] where i =0,..  and Buffers in parallel will 
have ID Bp[i] where i=0,...  Machines in series system will have ID M[i][j] i,j=0,.. and 
buffers in series will have id B_src_dest where src is the position of src machine and dest 
is the position of destination machine. All other buffers are named with ID Bi where i=1,2,3.."""

# importing required libraries
import simpy, sys, os
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Class for System A: Mp_in -> 10 Parallel Machines -> Mp_out
class SystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing Mp_in with Round Robin logic for splitting
        self.Mp_in = Machine(env, id="Mp_in", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.Mp_in)
        
        # Initializing 10 parallel machines Mp[i]
        self.Mp = [Machine(env, id=f"Mp[{i}]") for i in range(10)]
        self.add_child_node(self.Mp)
        
        # Initializing Mp_out
        # It uses Round Robin because the last System A block feeds 5 System B rows
        self.Mp_out = Machine(env, id="Mp_out", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.Mp_out)
        
        # Edges for splitting: Mp_in -> Mp[i]
        # Naming convention: Bp[i]
        self.split_edges = [Buffer(env, id=f"Bp[{i}]") for i in range(10)]
        self.add_child_edge(self.split_edges)
        
        # Edges for merging: Mp[i] -> Mp_out
        # Naming convention: Bi (starting from 1)
        self.merge_edges = [Buffer(env, id=f"B{i+1}") for i in range(10)]
        self.add_child_edge(self.merge_edges)
        
        # Connecting Mp_in to Mp[i]
        for i in range(10):
            self.split_edges[i].connect(self.Mp_in, self.Mp[i])
            
        # Connecting Mp[i] to Mp_out
        for i in range(10):
            self.merge_edges[i].connect(self.Mp[i], self.Mp_out)
            
        # Exposing source and sink of this block
        self.source = self.Mp_in
        self.sink = self.Mp_out

# Class for System B: 10 Machines in Series
class SystemB(Node):
    def __init__(self, env, id, row_index):
        super().__init__(env, id)
        
        # Initializing 10 machines in series M[i][j]
        self.M = [Machine(env, id=f"M[{row_index}][{j}]") for j in range(10)]
        self.add_child_node(self.M)
        
        # Initializing buffers in series
        # Naming convention: B_src_dest
        self.edges = []
        for j in range(9):
            buf = Buffer(env, id=f"B_{j}_{j+1}")
            self.edges.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.M[j], self.M[j+1])
            
        # Exposing source and sink of this block
        self.source = self.M[0]
        self.sink = self.M[9]

# Main System Model
class MainSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing Source
        self.src = Source(env, id="Source")
        self.add_child_node(self.src)
        
        # Initializing 5 System A blocks
        self.sysA = [SystemA(env, id=f"SystemA[{i}]") for i in range(5)]
        self.add_child_node(self.sysA)
        
        # Initializing 5 System B rows
        self.sysB = [SystemB(env, id=f"SystemB[{i}]", row_index=i) for i in range(5)]
        self.add_child_node(self.sysB)
        
        # Initializing Sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)
        
        # Connecting Source to first System A
        # Naming convention: Bi
        self.edge_src = Buffer(env, id="B1")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.src, self.sysA[0].source)
        
        # Connecting System A blocks in series
        self.inter_A_edges = []
        edge_counter = 2
        for i in range(4):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.inter_A_edges.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.sysA[i].sink, self.sysA[i+1].source)
            edge_counter += 1
            
        # Connecting last System A to all System B rows
        self.A_to_B_edges = []
        for i in range(5):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.A_to_B_edges.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.sysA[4].sink, self.sysB[i].source)
            edge_counter += 1
            
        # Connecting all System B rows to Sink
        self.B_to_sink_edges = []
        for i in range(5):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.B_to_sink_edges.append(buf)
            self.add_child_edge(buf)
            buf.connect(self.sysB[i].sink, self.sink)
            edge_counter += 1

# Initializing SimPy environment
env = simpy.Environment()
# Creating the top-level system
TOP = MainSystem(env, "TOP")
# Filling hierarchical IDs
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)