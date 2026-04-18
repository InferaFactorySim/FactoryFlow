"""
ModelDescription:
There are five linear homogenous serial systems in parallel. First, and fourth series have 5 machines each, 2nd and 5th have 4. 3rd have 3 machine. There is interconnection between row1.M2 to row2.m2  , row3.m3 to row4.m4. row4.m1 to row5.m2. All machines are name as M[i+1], i is the position. and all buffers as B[i+1], i is the position.  All machines have a processing_Delay of 2 and buffers have a capacity of 2.  The src has a interarrival time of 0.3. All machines with multiple input edges will gave a work_capacity of 2. USe ID B[i+1] for all buffers in the model, Use ID Bi i=1,2,3 for all buffers outside LinearRow class.



 MODEL ASSUMPTIONS:
1. Node names and Types for machines and buffers within the rows are chosen according to the user's description.
2. Added a common Source node named 'src' and a common Sink node named 'sink' to the system to facilitate flow, as these were not specified in the description.
3. Connected the common Source to the first machine (M[0]) of each of the five rows using a single buffer for each connection.
4. Connected the last machine of each of the five rows to the common Sink using a single buffer for each connection.
5. Used default edge type 'Buffer' for all connections ( intra-row) as edge types were not specified. Buffer ID is "B[i+1]". Used default edge type 'Buffer' for all connections ( intra-row) as edge types were not specified. Buffer ID is "Bi" where i=1,2,3 for buffers connecting src to machine in linear row and last machine in row to sink.
6. Used a single buffer for every connection between nodes, as the number of buffers was not specified.
7. Used default values for all missing parameters (processing delays, buffer capacities, source inter-arrival times) for all components.
8. Inferred a repeated pattern for the linear rows and assumed a parameterized class (e.g., `LinearRow`) will be created and instantiated 5 times with machine counts of 5, 4, 3, 5, and 4 respectively.
9. Mapped row references (row1 through row5) to 0-based indices (index 0 through 4) for implementation.
10. Interpreted machine references in the interconnections (e.g., M2, M3) as referring to the specific Machine ID (e.g., M[2], M[3]) within that row.
11. Assumed the direction of flow for interconnections is from the first mentioned node to the second (e.g., from row1.M2 to row2.m2).
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# defining the linear row model
class LinearRow(Node):
    def __init__(self, env, id, n_machines=5, high_cap_indices=None):
        super().__init__(env, id)
        if high_cap_indices is None:
            high_cap_indices = []
            
        # creating machines
        # ID is M[i+1], processing_delay is 2
        # work_capacity is 2 for machines with multiple inputs (specified by high_cap_indices), else 1
        self.machines = []
        for i in range(n_machines):
            cap = 2 if i in high_cap_indices else 1
            self.machines.append(Machine(env, id=f"M[{i+1}]", processing_delay=2, work_capacity=cap))
        self.add_child_node(self.machines)
        
        # creating buffers within the row
        # ID is B[i+1], capacity is 2
        self.buffers = []
        for i in range(n_machines - 1):
            b = Buffer(env, id=f"B[{i+1}]", capacity=2)
            self.buffers.append(b)
            b.connect(self.machines[i], self.machines[i+1])
        self.add_child_edge(self.buffers)

# defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # initializing common source
        self.src = Source(env, id="src", inter_arrival_time=0.3)
        self.add_child_node(self.src)
        
        # initializing common sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # defining row configurations: (machine_count, high_capacity_indices)
        # Row 1: 5 machines
        # Row 2: 4 machines, M2 (index 1) has multiple inputs
        # Row 3: 3 machines
        # Row 4: 5 machines, M4 (index 3) has multiple inputs
        # Row 5: 4 machines, M2 (index 1) has multiple inputs
        row_configs = [
            (5, []),
            (4, [1]),
            (3, []),
            (5, [3]),
            (4, [1])
        ]
        
        # creating rows
        self.rows = []
        for i, (n, high_cap) in enumerate(row_configs):
            self.rows.append(LinearRow(env, id=f"row{i+1}", n_machines=n, high_cap_indices=high_cap))
        self.add_child_node(self.rows)
        
        self.ext_buffers = []
        buf_id_counter = 1
        
        # connecting source to first machine of each row
        for r in self.rows:
            b = Buffer(env, id=f"B{buf_id_counter}", capacity=2)
            buf_id_counter += 1
            self.ext_buffers.append(b)
            b.connect(self.src, r.machines[0])
            
        # connecting last machine of each row to sink
        for r in self.rows:
            b = Buffer(env, id=f"B{buf_id_counter}", capacity=2)
            buf_id_counter += 1
            self.ext_buffers.append(b)
            b.connect(r.machines[-1], self.sink)
            
        # connecting rows based on description
        # row1.M2 -> row2.M2 (indices: row 0, mach 1 -> row 1, mach 1)
        # row3.M3 -> row4.M4 (indices: row 2, mach 2 -> row 3, mach 3)
        # row4.M1 -> row5.M2 (indices: row 3, mach 0 -> row 4, mach 1)
        interconnections = [
            (0, 1, 1, 1),
            (2, 2, 3, 3),
            (3, 0, 4, 1)
        ]
        
        for r_src, m_src, r_dst, m_dst in interconnections:
            b = Buffer(env, id=f"B{buf_id_counter}", capacity=2)
            buf_id_counter += 1
            self.ext_buffers.append(b)
            
            src_node = self.rows[r_src].machines[m_src]
            dst_node = self.rows[r_dst].machines[m_dst]
            
            b.connect(src_node, dst_node)
            
        self.add_child_edge(self.ext_buffers)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating model
TOP.validate()
# running simulation
TOP.run_simulation(25)