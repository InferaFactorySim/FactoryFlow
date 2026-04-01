"""
ModelDescription:
10 machines are connected in series. Use'src' as id  for source and 'sink' as id  for sink. 
Name machines  M00,M01,..M09 5th machine has work_capacity=3, others all work_capacity=1.  
Between 5th(M04) and 6th(M05) machine there are four buffers.All buffers have store capacity=2, 
except the buffer between 5th and 6th machines. Those have a store capacity=4. named 
B_04_05_1,B_04_05_2,.. B04_05_4   Other buffers as B_src_00, B_01_02,B_02_03,..B_09_sink.
There are ten such series. Machine in row 1 will be M00,M01,..M09 Machines in second row 
will be M10,M11,...M29.  in 3rd row M20, M21,..  Machines in last row will be named 
M90,M91,..M99 and Buffers as B_src_90, B_91_92,B_92_3,..B_99_sink   B_24_25_1,B_24_25_2,.. 
are between M24 and M25. In all rows there are 4 buffers between 5th machine and 6th Machine 
as explained above. That is  B_14_15_1,B_14_15_2,B_14_15_3,B_14_15_4 are between M14 and M15. 
buffers between 5th and 6th machine as named B_94_95_1,B_94_95_2,B_94_95_3,B_94_95_4 B_94_95_4 
are between src_node- M94 and dest_node-M95. 

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
        self.src = Source(env, id="src")
        self.add_child_node(self.src)
        
        # initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        self.rows = []
        
        # Creating 10 rows of machines
        for r in range(10):
            row_machines = []
            for m in range(10):
                # Machine naming M00 to M99
                m_id = f"M{r}{m}"
                
                # 5th machine (index 4) has specific properties
                if m == 4:
                    # work_capacity=3, out_edge_selection="ROUND_ROBIN" for parallel buffers
                    machine = Machine(env, id=m_id, work_capacity=3, out_edge_selection="ROUND_ROBIN")
                else:
                    # others work_capacity=1
                    machine = Machine(env, id=m_id, work_capacity=1)
                
                row_machines.append(machine)
            
            self.rows.append(row_machines)
            self.add_child_node(row_machines)

        # Creating edges
        
        # 1. Connecting Source to the first machine of each row
        for r in range(10):
            # Buffer name B_src_{row}0
            b_name = f"B_src_{r}0"
            # Default capacity 2
            buf = Buffer(env, id=b_name, capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.src, self.rows[r][0])
            
        # 2. Connecting machines within each row
        for r in range(10):
            for m in range(9): # Connect M[m] to M[m+1]
                # Check if connection is between 5th (index 4) and 6th (index 5) machine
                if m == 4:
                    # 4 parallel buffers with capacity 4
                    for k in range(1, 5):
                        b_name = f"B_{r}4_{r}5_{k}"
                        buf = Buffer(env, id=b_name, capacity=4)
                        self.add_child_edge(buf)
                        buf.connect(self.rows[r][m], self.rows[r][m+1])
                else:
                    # Standard single buffer with capacity 2
                    b_name = f"B_{r}{m}_{r}{m+1}"
                    buf = Buffer(env, id=b_name, capacity=2)
                    self.add_child_edge(buf)
                    buf.connect(self.rows[r][m], self.rows[r][m+1])
                    
        # 3. Connecting the last machine of each row to Sink
        for r in range(10):
            # Buffer name B_{row}9_sink
            b_name = f"B_{r}9_sink"
            # Default capacity 2
            buf = Buffer(env, id=b_name, capacity=2)
            self.add_child_edge(buf)
            buf.connect(self.rows[r][9], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating the system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)