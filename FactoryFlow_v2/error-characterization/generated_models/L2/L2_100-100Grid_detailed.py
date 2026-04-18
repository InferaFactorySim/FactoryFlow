"""
Description:
100 machines are connected in series. Use'src00' as id  for source and 'sink00' as id  for sink in row1. Name machines  src00,M[00][00],M[00][01],..M[00][99],sink00. Buffers as B_src00_[00][00],B_[00][00]_[00][01],  B_[00][01]_[00][02],B_[00][02]_[00][03],..B_[00][99]_sink00.
There are 100 such series. Machine in row 1 will be src00,M[00][00],M[00][01],..M[00][99],sink00  Machines in second row will be src01,M[01][00],M[01][01],..M[01][99],sink01   in 3rd row src02,M[02][00],M[02][01],..M[02][99],sink02  Machines in last row will be named src99,M[99][00],M[99][01],..M[99][99],sink99  and Buffers as B_src99_[99][00],B_[99][00]_[99][01],  B_[99][01]_[99][02],B_[99][02]_[99][03],..B_[99][99]_sink99. Buffers are used to connect machines between two rows. B_[00][00]_[01][00] connects the first machines in row1 and row2.

ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
3. Assumed a single buffer is used wherever the number of buffers between nodes is not explicitly specified.
4. Inferred a repeated pattern of a linear sequence (row) containing a source, 100 machines, and a sink. A class will be created for this repeated pattern to instantiate the 100 rows.
5. Inferred the logical flow of inter-row buffers to be directed from row i to row i+1 (e.g., from M[00][00] to M[01][00]).
6. Assumed out_edge_selection="ROUND_ROBIN" for machines that have multiple outgoing edges (connecting to the next machine in the same row and the corresponding machine in the next row) to ensure equal splitting, as split ratios are not specified in the description.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class RowModel(Node):
    def __init__(self, env, id, row_idx, num_machines=100):
        super().__init__(env, id)
        r_str = f"{row_idx:02d}"
        
        self.source = Source(env, id=f"src{r_str}")
        self.add_child_node(self.source)
        
        self.M = [Machine(env, id=f"M[{r_str}][{j:02d}]", out_edge_selection="ROUND_ROBIN") for j in range(num_machines)]
        self.add_child_node(self.M)
        
        self.sink = Sink(env, id=f"sink{r_str}")
        self.add_child_node(self.sink)
        
        self.e_src = Buffer(env, id=f"B_src{r_str}_[{r_str}][00]")
        self.add_child_edge(self.e_src)
        self.e_src.connect(self.source, self.M[0])
        
        self.e_m = [Buffer(env, id=f"B_[{r_str}][{j:02d}]_[{r_str}][{j+1:02d}]") for j in range(num_machines-1)]
        self.add_child_edge(self.e_m)
        for j in range(num_machines-1):
            self.e_m[j].connect(self.M[j], self.M[j+1])
            
        self.e_sink = Buffer(env, id=f"B_[{r_str}][{num_machines-1:02d}]_sink{r_str}")
        self.add_child_edge(self.e_sink)
        self.e_sink.connect(self.M[-1], self.sink)

class SystemModel(Node):
    def __init__(self, env, id, num_rows=100, num_machines=100):
        super().__init__(env, id)
        
        self.rows = [RowModel(env, id=f"Row[{i:02d}]", row_idx=i, num_machines=num_machines) for i in range(num_rows)]
        self.add_child_node(self.rows)
        
        self.sources = [row.source for row in self.rows]
        self.sinks = [row.sink for row in self.rows]
        
        self.inter_e = []
        for i in range(num_rows - 1):
            r1_str = f"{i:02d}"
            r2_str = f"{i+1:02d}"
            row_edges = [Buffer(env, id=f"B_[{r1_str}][{j:02d}]_[{r2_str}][{j:02d}]") for j in range(num_machines)]
            self.add_child_edge(row_edges)
            for j in range(num_machines):
                row_edges[j].connect(self.rows[i].M[j], self.rows[i+1].M[j])
            self.inter_e.append(row_edges)

env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)