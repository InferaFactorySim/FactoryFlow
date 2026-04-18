"""
Description:
100 machines are connected in series. Use'src00' as id  for source and 'sink00' as id  
for sink in row1. Name machines  src00,M[00][00],M[00][01],..M[00][99],sink00. Buffers 
as B_src00_[00][00],B_[00][00]_[00][01],  B_[00][01]_[00][02],B_[00][02]_[00][03],..B_[00][99]_sink00.
There are 100 such series. Machine in row 1 will be src00,M[00][00],M[00][01],..M[00][99],
sink00  Machines in second row will be src01,M[01][00],M[01][01],..M[01][99],sink01 
in 3rd row src02,M[02][00],M[02][01],..M[02][99],sink02  Machines in last row will be 
named src99,M[99][00],M[99][01],..M[99][99],sink99  and Buffers as B_src99_[99][00],
B_[99][00]_[99][01],  B_[99][01]_[99][02],B_[99][02]_[99][03],..B_[99][99]_sink99. 
Buffers are used to connect machines between two rows. B_[00][00]_[01][00] connects the 
first machines in row1 and row2.

"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


#LINEAR SEQUENCE OF 100 MACHINES REPRESENTING ONE PRODUCTION ROW with source and sink
class Row(Node):
    def __init__(self, env, id, row_idx, num_machines=100):
        super().__init__(env, id)
        row_idx = f"{row_idx:02d}"
        
        self.source = Source(env, id=f"src{row_idx}")
        self.add_child_node(self.source)
        
        self.M = [Machine(env, id=f"M[{row_idx}][{j:02d}]", out_edge_selection="ROUND_ROBIN") for j in range(num_machines)]
        self.add_child_node(self.M)
        
        self.sink = Sink(env, id=f"sink{row_idx}")
        self.add_child_node(self.sink)
        
        self.buffer_src = Buffer(env, id=f"B_src{row_idx}_[{row_idx}][00]")
        self.add_child_edge(self.buffer_src)
        self.buffer_src.connect(self.source, self.M[0])
        
        self.buffer_inter = [Buffer(env, id=f"B_[{row_idx}][{j:02d}]_[{row_idx}][{j+1:02d}]") for j in range(num_machines-1)]
        self.add_child_edge(self.buffer_inter)
        for j in range(num_machines-1):
            self.buffer_inter[j].connect(self.M[j], self.M[j+1])
            
        self.buffer_sink = Buffer(env, id=f"B_[{row_idx}][{num_machines-1:02d}]_sink{row_idx}")
        self.add_child_edge(self.buffer_sink)
        self.buffer_sink.connect(self.M[-1], self.sink)

# 100 rows of linear sequences with inter-row buffers between corresponding machines.
class SystemModel(Node):
    def __init__(self, env, id, num_rows=100, num_machines=100):
        super().__init__(env, id)
        
        self.rows = [Row(env, id=f"Row[{i:02d}]", row_idx=i, num_machines=num_machines) for i in range(num_rows)]
        self.add_child_node(self.rows)
        
        self.sources = [row.source for row in self.rows]
        self.sinks = [row.sink for row in self.rows]
        
        
        for i in range(num_rows - 1):
            row1_id = f"{i:02d}"
            row2_id = f"{i+1:02d}"
            row_edges = [Buffer(env, id=f"B_[{row1_id}][{j:02d}]_[{row2_id}][{j:02d}]") for j in range(num_machines)]
            self.add_child_edge(row_edges)
            for j in range(num_machines):
                row_edges[j].connect(self.rows[i].M[j], self.rows[i+1].M[j])
            

env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)