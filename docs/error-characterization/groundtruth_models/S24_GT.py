"""There is a mesh of 10X10 machines with a common source and a common sink. The edges flow right and 
down. There is no machine at 4th row and 3rd column, and from 2nd to 5th column in 6th row. This means 
the edges directly connect to the next element skipping the absent machines horizontally. Vertically 
if there is no machine skip that connection. The source having delay of 1. Machine IDs are M[1], M[2],... 
and buffer IDs are B1,B2,.. Let all machines have processing_delay of 2.353 and a work_capacity of 1. 
let all buffers be of capacity=3.All machines with multiple input edges will gave a work_capacity of 3"""

import simpy
#import factorysimpy
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..','..','src')))

from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer    
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink






# Class representing a single row of the mesh
class RowSubsystem(Node):
    def __init__(self, env, id, row_idx, missing_cols):
        super().__init__(env, id)
        self.row_idx = row_idx
        self.machines_by_col = {}
        self.ordered_machines = []
        
        # Create machines for columns 1 to 10, skipping missing ones
        for col in range(1, 11):
            if col in missing_cols:
                continue
            
            # Machine ID format: M[row][col]
            m_id = f"M[{row_idx}][{col}]"
            # Default work_capacity is 1, updated later if multiple inputs exist
            m = Machine(env, id=m_id, processing_delay=2.353, work_capacity=1)
            self.machines_by_col[col] = m
            self.ordered_machines.append(m)
            
        self.add_child_node(self.ordered_machines)
        
        # Create horizontal edges connecting machines in the row
        self.horiz_edges = []
        for i in range(len(self.ordered_machines) - 1):
            m_curr = self.ordered_machines[i]
            m_next = self.ordered_machines[i+1]
            
            # Extract column indices for buffer naming
            c_curr = int(m_curr.id.split('][')[1].strip(']'))
            c_next = int(m_next.id.split('][')[1].strip(']'))
            
            # Buffer ID format: B_{r}{c1}_{r}{c2}
            b_id = f"B_{row_idx}{c_curr}_{row_idx}{c_next}"
            b = Buffer(env, id=b_id, capacity=3)
            b.connect(m_curr, m_next)
            self.horiz_edges.append(b)
            
        self.add_child_edge(self.horiz_edges)

# Class representing the full 10x10 mesh system
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create common Source and Sink
        self.source = Source(env, id="src", inter_arrival_time=1)
        self.sink = Sink(env, id="sink")
        self.add_child_node([self.source, self.sink])
        
        # Define missing machines based on description
        # Row 5: 4th column missing
        # Row 7: 3rd to 6th columns missing
        missing_map = {
            5: {4},
            7: {3, 4, 5, 6}
        }
        
        # Create Row Subsystems
        self.rows = []
        for r in range(1, 11):
            missing = missing_map.get(r, set())
            row_sub = RowSubsystem(env, id=f"Row_{r}", row_idx=r, missing_cols=missing)
            self.rows.append(row_sub)
        self.add_child_node(self.rows)
        
        self.source_edges = []
        self.sink_edges = []
        self.vert_edges = []
        
        # Create connections: Source, Sink, and Vertical
        for r_idx, row in enumerate(self.rows):
            r = r_idx + 1
            
            # Connect Source to the first machine of the row
            if row.ordered_machines:
                first_m = row.ordered_machines[0]
                c_first = int(first_m.id.split('][')[1].strip(']'))
                b_src = Buffer(env, id=f"B_src_{r}{c_first}", capacity=3)
                b_src.connect(self.source, first_m)
                self.source_edges.append(b_src)
                
                # Connect the last machine of the row to Sink
                last_m = row.ordered_machines[-1]
                c_last = int(last_m.id.split('][')[1].strip(']'))
                b_sink = Buffer(env, id=f"B_{r}{c_last}_sink", capacity=3)
                b_sink.connect(last_m, self.sink)
                self.sink_edges.append(b_sink)
            
            # Create vertical connections to the next row
            if r < 10:
                next_row = self.rows[r_idx + 1]
                for col, m_curr in row.machines_by_col.items():
                    # Connect only if the machine exists in the same column in the next row
                    if col in next_row.machines_by_col:
                        m_next = next_row.machines_by_col[col]
                        b_vert = Buffer(env, id=f"B_{r}{col}_{r+1}{col}", capacity=3)
                        b_vert.connect(m_curr, m_next)
                        self.vert_edges.append(b_vert)
        
        self.add_child_edge(self.source_edges)
        self.add_child_edge(self.sink_edges)
        self.add_child_edge(self.vert_edges)
        
        # Update work_capacity for machines with multiple input edges
        for r_idx, row in enumerate(self.rows):
            r = r_idx + 1
            for col, m in row.machines_by_col.items():
                input_count = 0
                
                # Check Horizontal/Source Input
                first_col = int(row.ordered_machines[0].id.split('][')[1].strip(']'))
                if col == first_col:
                    input_count += 1 # Input from Source
                else:
                    input_count += 1 # Input from Left Machine
                
                # Check Vertical Input
                if r > 1:
                    prev_row = self.rows[r_idx - 1]
                    if col in prev_row.machines_by_col:
                        input_count += 1 # Input from Above Machine
                
                # If multiple inputs, set capacity to 3
                if input_count > 1:
                    m.work_capacity = 3

      
    
       


        
        

# initializing simpy environment
env = simpy.Environment()

# creating system model
TOP = SystemModel(env, "TOP")


TOP.fill_hierarchical_id()

#import factorysimpy
from factorysimpy.utils import utils



fig = utils.draw_blockdiagram(TOP)
path = fig.render(filename="S24_GT_new", directory=".", format="png", cleanup=True)
TOP.validate()
TOP.show_hierarchy()
TOP.run_simulation(25)

        









