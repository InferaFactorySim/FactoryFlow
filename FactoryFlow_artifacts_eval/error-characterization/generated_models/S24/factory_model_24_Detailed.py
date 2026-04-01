"""
ModelDescription:
There is a mesh of 10X10 machines with a common source and a common sink. The edges flow right and down. There is no machine at 5th row and 4th column, and from 3rd to 6th column in 7th row. This means the edges directly connect to the next element skipping the absent machines horizontally. Vertically if there is no machine skip that connection. The source having delay of 1. Machine IDs are M[1][1], M[1][2],... and buffer IDs are B_11_12,B_11_21, .. Let all machines have processing_delay of 2.353 and a work_capacity of 1. let all buffers be of capacity=3.All machines with multiple input edges will gave a work_capacity of 3.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Assumed Source ID is "source" and Sink ID is "sink".
3. Assumed the Source connects to the top-left machine M[1][1] via a buffer.
4. Assumed the bottom-right machine M[10][10] connects to the Sink via a buffer.
5. Used a single buffer for all connections between nodes.
6. Assumed Buffer IDs follow the format `B_{r1}_{c1}_{r2}_{c2}` representing a connection from M[r1][c1] to M[r2][c2].
7. Assumed `out_edge_selection` is set to "ROUND_ROBIN" for all machines having multiple outgoing edges (Right and Down).
8. Assumed "Source having delay of 1" refers to the `inter_arrival_time` parameter.
9. Assumed machines receiving inputs from both a horizontal neighbor and a vertical neighbor have a `work_capacity` of 3, while others (including those where a neighbor is missing or the connection is skipped) have a `work_capacity` of 1.
10. Due to the specific coordinate-based gaps (missing machines) preventing uniform row patterns, assumed the system is built directly in the main class without creating a repeated "Row" subclass.
"""

# importing required libraries
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
        
        # initializing source
        self.source = Source(env, id="source", inter_arrival_time=1)
        self.add_child_node(self.source)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Grid setup
        rows = 10
        cols = 10
        self.grid = [[None for _ in range(cols)] for _ in range(rows)]
        self.machines = []
        
        # Creating machines
        for r in range(rows):
            for c in range(cols):
                # Check missing machines
                # 5th row (index 4), 4th column (index 3)
                if r == 4 and c == 3:
                    continue
                # 7th row (index 6), 3rd to 6th column (indices 2 to 5)
                if r == 6 and (2 <= c <= 5):
                    continue
                
                # Determine work_capacity based on inputs
                input_count = 0
                
                # Input from Source
                if r == 0 and c == 0:
                    input_count += 1
                
                # Input from Left (Horizontal)
                # Find nearest existing neighbor to the left
                has_left = False
                for k in range(c - 1, -1, -1):
                    if self.grid[r][k] is not None:
                        has_left = True
                        break
                if has_left:
                    input_count += 1
                
                # Input from Top (Vertical)
                # Check immediate neighbor above
                if r > 0 and self.grid[r-1][c] is not None:
                    input_count += 1
                
                capacity = 3 if input_count > 1 else 1
                
                # Create machine
                m_id = f"M[{r+1}][{c+1}]"
                m = Machine(env, id=m_id, processing_delay=2.353, work_capacity=capacity, out_edge_selection="ROUND_ROBIN")
                self.grid[r][c] = m
                self.machines.append(m)
        
        self.add_child_node(self.machines)
        
        # Creating edges
        self.buffers = []
        
        # Connect Source to M[1][1]
        if self.grid[0][0] is not None:
            b_src = Buffer(env, id="B_source_1_1", capacity=3)
            b_src.connect(self.source, self.grid[0][0])
            self.buffers.append(b_src)
            self.add_child_edge(b_src)
            
        # Connect Grid
        for r in range(rows):
            for c in range(cols):
                curr = self.grid[r][c]
                if curr is None:
                    continue
                
                # Horizontal Connection (Right)
                # Find next existing machine in the row
                next_col = -1
                for k in range(c + 1, cols):
                    if self.grid[r][k] is not None:
                        next_col = k
                        break
                
                if next_col != -1:
                    dest = self.grid[r][next_col]
                    b_id = f"B_{r+1}_{c+1}_{r+1}_{next_col+1}"
                    buf = Buffer(env, id=b_id, capacity=3)
                    buf.connect(curr, dest)
                    self.buffers.append(buf)
                    self.add_child_edge(buf)
                
                # Vertical Connection (Down)
                # Check immediate neighbor below
                if r < rows - 1:
                    dest = self.grid[r+1][c]
                    if dest is not None:
                        b_id = f"B_{r+1}_{c+1}_{r+2}_{c+1}"
                        buf = Buffer(env, id=b_id, capacity=3)
                        buf.connect(curr, dest)
                        self.buffers.append(buf)
                        self.add_child_edge(buf)
        
        # Connect M[10][10] to Sink
        if self.grid[9][9] is not None:
            b_sink = Buffer(env, id="B_10_10_sink", capacity=3)
            b_sink.connect(self.grid[9][9], self.sink)
            self.buffers.append(b_sink)
            self.add_child_edge(b_sink)

# initiliating simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids from TOP
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)