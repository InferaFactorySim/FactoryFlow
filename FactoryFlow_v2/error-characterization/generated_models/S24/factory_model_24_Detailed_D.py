"""
ModelDescription:
There is a mesh of 10X10 machines with a common  source and a common  sink . The edges flow right and down. There is no machine at 5th row and 4th column, and from 3rd to 6th column in 7th row. This means the edges directly connect to the next element skipping the absent machines horizontally. Vertically if there is no machine skip that connection. The source having delay of 1. Machine IDs are M[1][1], M[1][2],... and buffer IDs are B_11_12,B_11_21, .. Let all machines have processing_delay of 2.353 and a work_capacity of 1. let all buffers be of capacity=3.All machines with multiple input edges will gave a work_capacity of 3. every row is a subsystem.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Assumed Source ID is "src" and Sink ID is "sink".
3. Assumed the common Source connects to the first machine of every row (M[row][1]) using a buffer.
4. Assumed the last machine of every row (M[row][10]) connects to the common Sink using a buffer.
5. Assumed vertical edges connect M[row][col] to M[row+1][col] using a buffer, provided both machines exist.
6. Assumed a single buffer is used for every connection between nodes.
7. Assumed Buffer IDs follow the format `B_{r1}{c1}_{r2}{c2}` (e.g., B_11_12) for connections between machines, and `B_src_{r}{c}` / `B_{r}{c}_sink` for source/sink connections.
8. Assumed default `out_edge_selection` (Round Robin) is used for machines with multiple outgoing edges (connecting both Right and Down).
9. Created a class `RowSubsystem` to represent the repeated row pattern, exposing machines to allow vertical connections at the system level.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class RowSubsystem(Node):
    def __init__(self, env, id, row_idx):
        super().__init__(env, id)
        self.row_idx = row_idx
        self.machines = {} 
        self.valid_cols = []
        
        # Identify valid columns based on missing machine logic
        for c in range(1, 11):
            # Skip (5, 4)
            if self.row_idx == 5 and c == 4:
                continue
            # Skip (7, 3) to (7, 6)
            if self.row_idx == 7 and (3 <= c <= 6):
                continue
            self.valid_cols.append(c)
            
        self.machine_nodes = []
        
        for c in self.valid_cols:
            # Determine work_capacity
            # Capacity is 3 if multiple inputs. 
            # Inputs = Horizontal (always 1) + Vertical (1 if machine above exists).
            # Check if machine above exists
            has_upper = False
            if self.row_idx > 1:
                prev_r = self.row_idx - 1
                # Check if prev_r, c is missing
                missing_prev = False
                if prev_r == 5 and c == 4: missing_prev = True
                if prev_r == 7 and (3 <= c <= 6): missing_prev = True
                
                if not missing_prev:
                    has_upper = True
            
            cap = 3 if has_upper else 1
            
            m_id = f"M[{self.row_idx}][{c}]"
            m = Machine(env, id=m_id, processing_delay=2.353, work_capacity=cap)
            self.machines[c] = m
            self.machine_nodes.append(m)
            
        self.add_child_node(self.machine_nodes)
        
        # Horizontal connections
        self.horiz_buffers = []
        for i in range(len(self.valid_cols) - 1):
            c1 = self.valid_cols[i]
            c2 = self.valid_cols[i+1]
            buf_id = f"B_{self.row_idx}{c1}_{self.row_idx}{c2}"
            b = Buffer(env, id=buf_id, capacity=3)
            self.horiz_buffers.append(b)
            b.connect(self.machines[c1], self.machines[c2])
            
        self.add_child_edge(self.horiz_buffers)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Common Source
        self.source = Source(env, id="src", inter_arrival_time=1)
        self.add_child_node(self.source)
        
        # Common Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Create Rows
        self.rows = []
        for r in range(1, 11):
            row_sub = RowSubsystem(env, id=f"Row_{r}", row_idx=r)
            self.rows.append(row_sub)
        self.add_child_node(self.rows)
        
        # Connect Source to first machine of each row
        self.src_buffers = []
        for r in range(10):
            row_obj = self.rows[r]
            if row_obj.valid_cols:
                first_c = row_obj.valid_cols[0]
                m = row_obj.machines[first_c]
                buf_id = f"B_src_{r+1}{first_c}"
                b = Buffer(env, id=buf_id, capacity=3)
                self.src_buffers.append(b)
                b.connect(self.source, m)
        self.add_child_edge(self.src_buffers)
        
        # Connect last machine of each row to Sink
        self.sink_buffers = []
        for r in range(10):
            row_obj = self.rows[r]
            if row_obj.valid_cols:
                last_c = row_obj.valid_cols[-1]
                m = row_obj.machines[last_c]
                buf_id = f"B_{r+1}{last_c}_sink"
                b = Buffer(env, id=buf_id, capacity=3)
                self.sink_buffers.append(b)
                b.connect(m, self.sink)
        self.add_child_edge(self.sink_buffers)
        
        # Vertical connections between rows
        self.vert_buffers = []
        for r in range(9): # 0 to 8 (Rows 1..9)
            row_curr = self.rows[r]
            row_next = self.rows[r+1]
            
            # Iterate columns 1 to 10
            for c in range(1, 11):
                # Connect if machine exists in both current and next row at column c
                if c in row_curr.machines and c in row_next.machines:
                    m_up = row_curr.machines[c]
                    m_down = row_next.machines[c]
                    
                    # ID: B_{r_curr}{c}_{r_next}{c}
                    # r is 0-based index, so row IDs are r+1 and r+2
                    buf_id = f"B_{r+1}{c}_{r+2}{c}"
                    b = Buffer(env, id=buf_id, capacity=3)
                    self.vert_buffers.append(b)
                    b.connect(m_up, m_down)
        self.add_child_edge(self.vert_buffers)

# Simulation
env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)