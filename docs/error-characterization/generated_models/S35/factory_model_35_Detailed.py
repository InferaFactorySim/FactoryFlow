"""
ModelDescription:
A systemA with  machine (Mp_in)  that splits into 10 machines  and the output from these machines ends in another a machine  (Mp_out) . There are 5 such systems that are connected in series .  There is another systemB with 10 machines in series and there are 5 such systems. the last machine in systemA is connected to the first machines in each row in systemB. Machines in parallel systems will have ID Mp[i] where i =0,..  and Buffers in parallel will have ID Bp[i] where i=0,...  Machines in series system will have ID M[i][j] i,j=0,.. and buffers in series will have id B_src_dest where src is the position of src machine and dest is the position of destination machine. All other buffers are named with ID Bi where i=1,2,3..

 MODEL ASSUMPTIONS:
1. Inferred the existence of a Source node to feed the input of the first SystemA and a Sink node to collect parts from the last machines of the SystemB rows, as these were not explicitly defined.
2. Used default edge type Buffer for all connections between machines and systems where the specific edge type was not mentioned.
3. Assumed a single buffer is used for every connection between nodes.
4. Used default values for all missing parameters including processing delays, buffer capacities, and source inter-arrival times.
5. Inferred out_edge_selection="ROUND_ROBIN" for the machine Mp_in (splitting to 10 parallel machines) and the final machine of the SystemA chain (splitting to 5 SystemB rows) to ensure equal distribution of flow.
6. Inferred a class-based structure where SystemA is defined as a reusable class (containing Mp_in, 10 parallel machines, and Mp_out) and SystemB is defined as a reusable class (containing 10 machines in series).
7. Inferred that inside SystemA, the 10 machines are arranged in parallel, receiving input from Mp_in and sending output to Mp_out.
8. Inferred that the 5 SystemA blocks are connected sequentially (Mp_out of one block to Mp_in of the next).
9. Inferred that the 5 SystemB blocks are arranged in parallel rows, and the last machines of all 5 SystemB rows connect to the common Sink.
10. Applied the naming convention Bp[i] to buffers connecting Mp_in to the parallel machines Mp[i], B_src_dest to buffers connecting machines within the SystemB series, and Bi to all remaining buffers (including merge buffers in SystemA, connections between SystemA blocks, and connections to Sink).
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class SystemA(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Machine Mp_in that splits into 10 machines
        # Inferred out_edge_selection="ROUND_ROBIN" for splitting
        self.Mp_in = Machine(env, id="Mp_in", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.Mp_in)
        
        # 10 machines in parallel with ID Mp[i]
        self.Mp = [Machine(env, id=f"Mp[{i}]") for i in range(10)]
        self.add_child_node(self.Mp)
        
        # Machine Mp_out
        self.Mp_out = Machine(env, id="Mp_out")
        self.add_child_node(self.Mp_out)
        
        # Buffers in parallel (Mp_in -> Mp[i]) with ID Bp[i]
        self.Bp = [Buffer(env, id=f"Bp[{i}]") for i in range(10)]
        self.add_child_edge(self.Bp)
        
        # Buffers from Mp[i] -> Mp_out with ID Bi (i=1..10)
        self.B_out = [Buffer(env, id=f"B{i+1}") for i in range(10)]
        self.add_child_edge(self.B_out)
        
        # Connections
        for i in range(10):
            self.Bp[i].connect(self.Mp_in, self.Mp[i])
            self.B_out[i].connect(self.Mp[i], self.Mp_out)
            
        # Define source and sink for this block
        self.source = self.Mp_in
        self.sink = self.Mp_out

class SystemB(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # 10 machines in series with ID M[i][j] where i is row_idx
        self.M = [Machine(env, id=f"M[{row_idx}][{j}]") for j in range(10)]
        self.add_child_node(self.M)
        
        # Buffers in series with ID B_src_dest
        self.B_series = []
        for j in range(9):
            buf = Buffer(env, id=f"B_{j}_{j+1}")
            self.add_child_edge(buf)
            buf.connect(self.M[j], self.M[j+1])
            self.B_series.append(buf)
            
        self.source = self.M[0]
        self.sink = self.M[-1]

class ManufacturingSystem(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # 5 SystemA blocks in series
        self.sysA = [SystemA(env, id=f"SystemA[{i}]") for i in range(5)]
        self.add_child_node(self.sysA)
        
        # 5 SystemB blocks in parallel (rows)
        self.sysB = [SystemB(env, id=f"SystemB[{i}]", row_idx=i) for i in range(5)]
        self.add_child_node(self.sysB)
        
        # Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Edges named Bi starting from 1 for all other buffers
        edge_counter = 1
        
        # Connect Source to first SystemA
        self.edge_src = Buffer(env, id=f"B{edge_counter}")
        self.add_child_edge(self.edge_src)
        self.edge_src.connect(self.src, self.sysA[0].source)
        edge_counter += 1
        
        # Connect SystemA blocks in series
        self.edges_A = []
        for i in range(4):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.add_child_edge(buf)
            buf.connect(self.sysA[i].sink, self.sysA[i+1].source)
            self.edges_A.append(buf)
            edge_counter += 1
            
        # Connect last SystemA to all SystemB blocks
        # Ensure last SystemA splits flow equally
        self.sysA[4].Mp_out.out_edge_selection = "ROUND_ROBIN"
        
        self.edges_A_B = []
        for i in range(5):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.add_child_edge(buf)
            buf.connect(self.sysA[4].sink, self.sysB[i].source)
            self.edges_A_B.append(buf)
            edge_counter += 1
            
        # Connect all SystemB blocks to Sink
        self.edges_B_Sink = []
        for i in range(5):
            buf = Buffer(env, id=f"B{edge_counter}")
            self.add_child_edge(buf)
            buf.connect(self.sysB[i].sink, self.sink)
            self.edges_B_Sink.append(buf)
            edge_counter += 1

# Initializing simpy environment
env = simpy.Environment()
# Creating the top level system
TOP = ManufacturingSystem(env, "TOP")
# Filling hierarchical ids
TOP.fill_hierarchical_id()
# Validating the model
TOP.validate()
# Running the simulation
TOP.run_simulation(25)