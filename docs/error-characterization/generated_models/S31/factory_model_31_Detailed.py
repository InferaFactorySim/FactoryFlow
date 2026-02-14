"""
ModelDescription:
10 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. Name machines  M00,M01,..M09 5th machine has work_capacity=3, others all work_capacity=1.  Between 5th(M04) and 6th(M05) machine there are four buffers.All buffers have store capacity=2, except the buffer between 5th and 6th machines. Those have a store capacity=4. named B_04_05_1,B_04_05_2,.. B04_05_4   Other buffers as B_src_00, B_01_02,B_02_03,..B_09_sink.
There are ten such series. Machine in row 1 will be M00,M01,..M09 Machines in second row will be M10,M11,...M29.  in 3rd row M20, M21,..  Machines in last row will be named M90,M91,..M99 and Buffers as B_src_90, B_91_92,B_92_3,..B_99_sink   B_24_25_1,B_24_25_2,.. are between M24 and M25. In all rows there are 4 buffers between 5th machine and 6th Machine as explained above. That is  B_14_15_1,B_14_15_2,B_14_15_3,B_14_15_4 are between M14 and M15. buffers between 5th and 6th machine as named B_94_95_1,B_94_95_2,B_94_95_3,B_94_95_4 B_94_95_4 are between src_node- M94 and dest_node-M95. 


 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a repeated pattern of a linear sequence of 10 machines and created a class for this pattern to be instantiated 10 times.
3. Used default values for processing_delay and inter_arrival_time for all components as they are not specified in the description.
4. Assumed `out_edge_selection` is Round Robin for the Source node (splitting to 10 rows) and the 5th machine in each row (splitting to 4 buffers) to distribute flow.
5. Assumed a single buffer is used for all connections between nodes (Source to Machine, Machine to Machine, Machine to Sink), except for the connection between the 5th and 6th machines where 4 buffers are explicitly specified.
"""

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
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
       
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)

        # Loop for 10 rows
        for r in range(10):
            # Create machines for the row
            row_machines = []
            for c in range(10):
                # 5th machine (index 4) has specific capacity and edge selection
                if c == 4:
                    m = Machine(env, id=f"M{r}{c}", work_capacity=3, out_edge_selection=1)
                else:
                    m = Machine(env, id=f"M{r}{c}", work_capacity=1)
                row_machines.append(m)
            
            # Add machines to child nodes
            self.add_child_node(row_machines)

            # Create edges
            
            # Buffer from Source to first machine
            b_src = Buffer(env, id=f"B_src_{r}0", capacity=2)
            self.add_child_edge(b_src)
            b_src.connect(self.src, row_machines[0])

            # Buffers between machines
            for c in range(9):
                if c == 4:
                    # 4 buffers between 5th and 6th machine with capacity 4
                    for k in range(1, 5):
                        b = Buffer(env, id=f"B_{r}4_{r}5_{k}", capacity=4)
                        self.add_child_edge(b)
                        b.connect(row_machines[c], row_machines[c+1])
                else:
                    # 1 buffer between other machines with capacity 2
                    b = Buffer(env, id=f"B_{r}{c}_{r}{c+1}", capacity=2)
                    self.add_child_edge(b)
                    b.connect(row_machines[c], row_machines[c+1])

            # Buffer from last machine to Sink
            b_sink = Buffer(env, id=f"B_{r}9_sink", capacity=2)
            self.add_child_edge(b_sink)
            b_sink.connect(row_machines[9], self.sink)

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