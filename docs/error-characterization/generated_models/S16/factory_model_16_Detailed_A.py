"""
ModelDescription:
Source_R1 feeds a logical 'Welding_Cell' via a buffer with ID B_src_R1. The cell contains Machine_W1, followed by Buffer_W (cap 5).  The outputs of the cells (from Machine_W1) connects to SINK_R1. There are three such cells in parallel rows R1,R2, R3 that are independent. All machines have a processing_Delay of 2. Each row can be inside a class R and intialised as R1, R2, R3

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. A class named `Welding_Cell` is created to represent the repeated pattern containing `Machine_W1` and `Buffer_W`.
3. Since the rows R1, R2, and R3 are described as independent, it is assumed that R2 and R3 have their own dedicated Sources (`Source_R2`, `Source_R3`), Input Buffers (`B_src_R2`, `B_src_R3`), and Sinks (`SINK_R2`, `SINK_R3`) following the pattern of R1.
4. The flow within the `Welding_Cell` is assumed to be `Machine_W1` feeding into `Buffer_W`.
5. The connection to the Sink is assumed to be from the output of the cell (`Buffer_W`) to the Sink, despite the description saying "from Machine_W1", as the buffer follows the machine.
6. Used default values for all missing parameters for all components (e.g., Source inter-arrival time, capacity of `B_src` buffers).
7. Used `Buffer` edges for all connections between nodes.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Welding_Cell(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Machine_W1 with processing delay of 2
        self.machine = Machine(env, id="Machine_W1", processing_delay=2)
        self.add_child_node(self.machine)
        
        # Buffer_W with capacity 5
        self.Buffer_W = Buffer(env, id="Buffer_W", capacity=5)
        self.add_child_edge(self.Buffer_W)

class R(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Source
        self.source = Source(env, id=f"Source_{id}")
        self.add_child_node(self.source)
        
        # Welding Cell
        self.cell = Welding_Cell(env, id="Welding_Cell")
        self.add_child_node(self.cell)
        
        # Sink
        self.sink = Sink(env, id=f"SINK_{id}")
        self.add_child_node(self.sink)
        
        # Buffer from Source to Cell
        self.b_src = Buffer(env, id=f"B_src_{id}")
        self.add_child_edge(self.b_src)
        
        # Connect Source to Machine inside Cell
        self.b_src.connect(self.source, self.cell.machine)
        
        # Connect Machine inside Cell to Sink via Buffer_W
        self.cell.Buffer_W.connect(self.cell.machine, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Create 3 rows R1, R2, R3
        self.rows = [R(env, id=f"R{i+1}") for i in range(3)]
        self.add_child_node(self.rows)

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