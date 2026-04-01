"""
ModelDescription:
A systemA with  machine that splits into 10 machines  and the output from these machines ends in another a machine. There are 5 such systems that are connected in series .  There is another systemB with 10 machines in series and there are 5 such systems. the last machine in systemA is connected to the first machines in each row in systemB. Machines in parallel systems will have ID Mp[i] where i =0,..  and Buffers in parallel will have ID Bp[i] where i=0,...  Machines in series system will have ID M[i][j] i,j=0,.. and buffers in series will have id B_src_dest where src is the position of src machine and dest is the position of destination machine. All other buffers are named with ID Bi where i=1,2,3..

 MODEL ASSUMPTIONS:
1. Inferred two reusable class definitions based on repeated patterns: "SystemA" (consisting of 1 split machine, 10 parallel machines, and 1 merge machine) and "SystemB" (consisting of 10 machines in series).
2. Added a Source node "src" connected to the input of the first SystemA block and a Sink node "sink" connected to the outputs of all 5 SystemB rows to complete the simulation flow, as these were not specified.
3. Interpreted the structure of SystemB as 5 parallel rows based on the phrase "connected to the first machines in each row", where each row contains 10 machines in series.
4. Used default edge type Buffer for all connections between machines and subsystems as edge type was not specified.
5. Used a single buffer for every connection between nodes where the number of buffers was not specified.
6. Inferred node names and IDs (e.g., "Mp_in", "Mp[i]", "Mp_out" where i is the position of the node for SystemA; "M[i][i]"  where i is the position of the node for SystemB) as they were not provided in the description.
7. Assumed out_edge_selection is "ROUND_ROBIN" for the splitting machine in SystemA and for the connection between the last SystemA block and the 5 parallel SystemB rows to ensure equal distribution.
8. Used default values for all missing parameters (processing delays, buffer capacities, inter-arrival times) for all components.
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
        
        # Split machine
        self.Mp_in = Machine(env, id="Mp_in", out_edge_selection="ROUND_ROBIN")
        self.add_child_node(self.Mp_in)
        
        # Parallel machines
        self.Mp = [Machine(env, id=f"Mp[{i}]") for i in range(10)]
        self.add_child_node(self.Mp)
        
        # Merge machine
        self.Mp_out = Machine(env, id="Mp_out")
        self.add_child_node(self.Mp_out)
        
        # Buffers in parallel
        # 10 buffers for split (Mp_in -> Mp[i]) and 10 buffers for merge (Mp[i] -> Mp_out)
        self.Bp = [Buffer(env, id=f"Bp[{i}]") for i in range(20)]
        self.add_child_edge(self.Bp)
        
        # Connect split
        for i in range(10):
            self.Bp[i].connect(self.Mp_in, self.Mp[i])
            
        # Connect merge
        for i in range(10):
            self.Bp[10+i].connect(self.Mp[i], self.Mp_out)
            
        self.source = self.Mp_in
        self.sink = self.Mp_out

class SystemB(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # Machines in series
        self.M = [Machine(env, id=f"M[{row_idx}][{j}]") for j in range(10)]
        self.add_child_node(self.M)
        
        # Buffers in series
        self.buffers = []
        for j in range(9):
            buf = Buffer(env, id=f"B_{j}_{j+1}")
            self.buffers.append(buf)
        self.add_child_edge(self.buffers)
        
        # Connect series
        for j in range(9):
            self.buffers[j].connect(self.M[j], self.M[j+1])
            
        self.source = self.M[0]
        self.sink = self.M[-1]

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # 5 SystemA blocks in series
        self.sysA = [SystemA(env, id=f"SystemA_Block[{i}]") for i in range(5)]
        self.add_child_node(self.sysA)
        
        # 5 SystemB rows in parallel
        self.sysB = [SystemB(env, id=f"SystemB_Row[{i}]", row_idx=i) for i in range(5)]
        self.add_child_node(self.sysB)
        
        # Global Buffers
        self.global_buffers = []
        b_idx = 1
        
        # Connect Source -> First SystemA
        b = Buffer(env, id=f"B{b_idx}")
        self.add_child_edge(b)
        b.connect(self.src, self.sysA[0].source)
        self.global_buffers.append(b)
        b_idx += 1
        
        # Connect SystemA blocks in series
        for i in range(4):
            b = Buffer(env, id=f"B{b_idx}")
            self.add_child_edge(b)
            b.connect(self.sysA[i].sink, self.sysA[i+1].source)
            self.global_buffers.append(b)
            b_idx += 1
            
        # Connect Last SystemA -> All SystemB rows
        # Set round robin on the last machine of the last SystemA block
        self.sysA[4].sink.out_edge_selection = "ROUND_ROBIN"
        
        for i in range(5):
            b = Buffer(env, id=f"B{b_idx}")
            self.add_child_edge(b)
            b.connect(self.sysA[4].sink, self.sysB[i].source)
            self.global_buffers.append(b)
            b_idx += 1
            
        # Connect All SystemB rows -> Sink
        for i in range(5):
            b = Buffer(env, id=f"B{b_idx}")
            self.add_child_edge(b)
            b.connect(self.sysB[i].sink, self.sink)
            self.global_buffers.append(b)
            b_idx += 1

env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)