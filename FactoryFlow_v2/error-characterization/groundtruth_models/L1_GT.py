"""
Description:
100 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink.
Name machines  M[00][00],M[00][01],..M[00][99]. Buffers as B_src_[00][00],B_[00][00]_[00][01],
B_[00][01]_[00][02],B_[00][02]_[00][03],..B_[00][99]_sink.There are 100 such series. Machine in row
1 will be M[00][00],M[00][01],..M[00][99]  Machines in second row will be M[01][00],M[01][01],..M[01][99]
in 3rd row M[02][00],M[02][01],..M[02][99]   Machines in last row will be named M[99][00],M[99][01],..M[99][99]
and Buffers as B_src_[99][00],B_[99][00]_[99][01],  B_[99][01]_[99][02],B_[99][02]_[99][03],..B_[99][99]_sink.
Source and sink are common for all lines

"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink


# Linear sequence of 100 machines representing one production row
class LinearSequence(Node):
    def __init__(self, env, id, row_index, num_machines=100):
        super().__init__(env, id)
        row_str = f"{row_index:02d}"

        self.M = [Machine(env, id=f"M[{row_str}][{col:02d}]") for col in range(num_machines)]
        self.add_child_node(self.M)

        self.buffers = [
            Buffer(env, id=f"B_[{row_str}][{col:02d}]_[{row_str}][{col+1:02d}]")
            for col in range(num_machines - 1)
        ]
        self.add_child_edge(self.buffers)

        for col in range(num_machines - 1):
            self.buffers[col].connect(self.M[col], self.M[col + 1])

        

# System model with 100 rows of linear sequences with common source and sink
class SystemModel(Node):
    def __init__(self, env, id, num_rows=100):
        super().__init__(env, id)

        

        self.lines = [LinearSequence(env, id=f"Line_{r:02d}", row_index=r) for r in range(num_rows)]
        self.add_child_node(self.lines)

        self.src_buffers  = [Buffer(env, id=f"B_src_[{r:02d}][00]")  for r in range(num_rows)]
        self.sink_buffers = [Buffer(env, id=f"B_[{r:02d}][99]_sink") for r in range(num_rows)]
        self.add_child_edge(self.src_buffers)
        self.add_child_edge(self.sink_buffers)


        self.source = Source(env, id="src", out_edge_selection="ROUND_ROBIN")
        self.sink   = Sink(env, id="sink")
        self.add_child_node([self.source, self.sink])

        for r in range(num_rows):
            self.src_buffers[r].connect(self.source, self.lines[r].M[0])
            self.sink_buffers[r].connect(self.lines[r].M[-1], self.sink)


env = simpy.Environment()
TOP = SystemModel(env, "TOP")
TOP.fill_hierarchical_id()
TOP.validate()
TOP.run_simulation(25)
