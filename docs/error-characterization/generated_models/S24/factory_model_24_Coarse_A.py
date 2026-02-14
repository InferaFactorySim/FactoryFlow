"""
ModelDescription:
There is a mesh of 10X10 machines with the source at top left and sink at bottom right. The edges flow right and down. There is no machine at 5th row and 4th column, and from 3rd to 6th column in 7th row. This means the edges directly connect to the next element skipping the absent machines. src and sink is common and the "src" connects to all first machines in the row and all last machines connects to "sink".  The series of machines are a subsystem. 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description (Source, Sink, Machine, Buffer).
2. Machines are identified using a coordinate-based naming convention (e.g., `M[row+1][col+1]`) corresponding to the 10x10 grid.
3. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
4. Used a single `Buffer` edge for every connection between nodes. 
5. The Source is assumed to connect to the machine at the top-left corner (row 0, column 0).
6. The machine at the bottom-right corner (row 9, column 9) is assumed to connect to the Sink.
7. Since Splitter nodes are not used, `Machine` nodes are assumed to handle output routing for flows that go both Right and Down, using a default `out_edge_selection` (e.g., Round Robin).
8. "Skipping absent machines" is assumed to mean that if the immediate neighbor in a direction (Right or Down) is missing, the edge connects to the next available machine in that same direction, bypassing the gap.
9. The entire mesh is treated as a single system pattern (SystemModel) containing the logic for the grid and the holes, rather than creating sub-classes for rows, due to the vertical connectivity and irregular gaps.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

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
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Grid dimensions
        self.rows = 10
        self.cols = 10
        
        # Absent machines coordinates (row_idx, col_idx)
        # 5th row, 4th column -> index (4, 3)
        # 7th row, 3rd to 6th column -> index (6, 2), (6, 3), (6, 4), (6, 5)
        self.absent_indices = {
            (4, 3),
            (6, 2), (6, 3), (6, 4), (6, 5)
        }
        
        self.machines = {} # Mapping (r, c) -> Machine object
        self.machine_list = [] # List for add_child_node
        
        # Creating machines
        for r in range(self.rows):
            for c in range(self.cols):
                if (r, c) in self.absent_indices:
                    continue
                
                # Machine ID: M[row+1][col+1]
                m_id = f"M[{r+1}][{c+1}]"
                m = Machine(env, id=m_id)
                self.machines[(r, c)] = m
                self.machine_list.append(m)
        
        # Adding machines to child nodes
        self.add_child_node(self.machine_list)
        
        self.buffers = []
        
        # Connecting machines
        for (r, c), m in self.machines.items():
            # Connect Right: Find next available machine in the same row
            for next_c in range(c + 1, self.cols):
                if (r, next_c) in self.machines:
                    target = self.machines[(r, next_c)]
                    # Buffer ID: B_{r1}{c1}_{r2}{c2}
                    b_id = f"B_{r+1}{c+1}_{r+1}{next_c+1}"
                    b = Buffer(env, id=b_id)
                    b.connect(m, target)
                    self.buffers.append(b)
                    self.add_child_edge(b)
                    break # Stop after connecting to the nearest neighbor
            
            # Connect Down: Find next available machine in the same column
            for next_r in range(r + 1, self.rows):
                if (next_r, c) in self.machines:
                    target = self.machines[(next_r, c)]
                    # Buffer ID: B_{r1}{c1}_{r2}{c2}
                    b_id = f"B_{r+1}{c+1}_{next_r+1}{c+1}"
                    b = Buffer(env, id=b_id)
                    b.connect(m, target)
                    self.buffers.append(b)
                    self.add_child_edge(b)
                    break # Stop after connecting to the nearest neighbor
        
        # Connect Source to Top-Left Machine (Assumption 5)
        if (0, 0) in self.machines:
            b_src = Buffer(env, id=f"B_src_11")
            b_src.connect(self.src, self.machines[(0, 0)])
            self.buffers.append(b_src)
            self.add_child_edge(b_src)
            
        # Connect Bottom-Right Machine to Sink (Assumption 6)
        if (9, 9) in self.machines:
            b_sink = Buffer(env, id=f"B_1010_sink")
            b_sink.connect(self.machines[(9, 9)], self.sink)
            self.buffers.append(b_sink)
            self.add_child_edge(b_sink)

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