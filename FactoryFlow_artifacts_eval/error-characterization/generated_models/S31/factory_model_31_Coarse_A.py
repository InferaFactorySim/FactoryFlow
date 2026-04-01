"""
ModelDescription:
The system consists of ten independent production lines arranged in parallel. Each production line contains ten machines connected in strict series, with a single source at the beginning and a single sink at the end. Source and sink are common for all lines. However, between the 5th machine and the 6th machine in every row, there are four parallel buffers instead of one. Machine in row 1 will be M00,M01,..M09 Machines in second row will be M10,M11,...M29.  in 3rd row M20, M21,..  Machines in last row will be named M90,M91,..M99 and Buffers as B_src_90, B_91_92,B_92_3,..B_99_sink   B_24_25_1,B_24_25_2,.. are between M24 and M25. In all rows there are 4 buffers between 5th machine and 6th Machine as explained above. That is  B_14_15_1,B_14_15_2,B_14_15_3,B_14_15_4 are between M14 and M15. buffers between 5th and 6th machine as named B_94_95_1,B_94_95_2,B_94_95_3,B_94_95_4 B_94_95_4 are between src_node- M94 and dest_node-M95. 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, capacities) for all components.
3. Inferred a repeated pattern for the production lines and created a class `ProductionLine` containing 10 machines to be instantiated 10 times.
4. Assumed a single buffer is used to connect machines in the series (e.g., Machine 1 to 2), except between the 5th and 6th machines where the specified 4 parallel buffers are used.
5. Assumed the common Source connects to the first machine of each of the 10 production lines via a separate buffer for each line.
6. Assumed the last machine of each of the 10 production lines connects to the common Sink via a separate buffer for each line.
7. Assumed default routing logic (Round Robin) for nodes with multiple output edges (Source and the 5th machine in each line) to distribute items.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class ProductionLine(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        
        # Create 10 machines for the row
        # Naming convention: M{row_idx}{machine_idx} (e.g., M00, M01... M99)
        self.machines = []
        for j in range(10):
            m_id = f"M{row_idx}{j}"
            self.machines.append(Machine(env, id=m_id))
        self.add_child_node(self.machines)
        
        self.internal_edges = []
        
        # Connect machines in series
        # Loop 0 to 8 to connect M[j] to M[j+1]
        for j in range(9):
            src_node = self.machines[j]
            dst_node = self.machines[j+1]
            
            # Suffixes for naming buffers
            src_suffix = f"{row_idx}{j}"
            dst_suffix = f"{row_idx}{j+1}"
            
            # Check if connection is between 5th machine (index 4) and 6th machine (index 5)
            if j == 4:
                # Create 4 parallel buffers
                for k in range(1, 5):
                    buf_id = f"B_{src_suffix}_{dst_suffix}_{k}"
                    buf = Buffer(env, id=buf_id)
                    self.internal_edges.append(buf)
                    buf.connect(src_node, dst_node)
            else:
                # Create single buffer
                buf_id = f"B_{src_suffix}_{dst_suffix}"
                buf = Buffer(env, id=buf_id)
                self.internal_edges.append(buf)
                buf.connect(src_node, dst_node)
                
        self.add_child_edge(self.internal_edges)
        
        # Expose first and last machines for connection to Source/Sink
        self.first_m = self.machines[0]
        self.last_m = self.machines[-1]

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source
        self.source = Source(env, id="src")
        self.add_child_node(self.source)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Create 10 parallel Production Lines
        self.lines = [ProductionLine(env, id=f"Line[{i}]", row_idx=i) for i in range(10)]
        self.add_child_node(self.lines)
        
        self.edges = []
        
        # Connect Source to the first machine of each line
        for i in range(10):
            dst_suffix = f"{i}0" # e.g., 00, 10, ... 90
            buf_id = f"B_src_{dst_suffix}"
            buf = Buffer(env, id=buf_id)
            self.edges.append(buf)
            buf.connect(self.source, self.lines[i].first_m)
            
        # Connect the last machine of each line to Sink
        for i in range(10):
            src_suffix = f"{i}9" # e.g., 09, 19, ... 99
            buf_id = f"B_{src_suffix}_sink"
            buf = Buffer(env, id=buf_id)
            self.edges.append(buf)
            buf.connect(self.lines[i].last_m, self.sink)
            
        self.add_child_edge(self.edges)

# Initializing simpy environment
env = simpy.Environment()

# Defining the top level system
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)