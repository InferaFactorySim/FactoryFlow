"""
ModelDescription:
Source_R1 feeds a logical 'Welding_Cell' via a buffer with ID B_src_R1. The cell contains Machine_W1, followed by Buffer_W (cap 5).  The outputs of the cells (from Machine_W1) connects to SINK_R1. There are three such cells in parallel rows R1,R2, R3 that are independent. All machines have a processing_Delay of 2.

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
        
        # Machine_W1
        self.machine = Machine(env, id="Machine_W1", processing_delay=2)
        self.add_child_node(self.machine)
        
        # Buffer_W (cap 5)
        self.buffer = Buffer(env, id="Buffer_W", capacity=5)
        self.add_child_edge(self.buffer)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        self.sources = []
        self.cells = []
        self.sinks = []
        self.input_buffers = []
        
        for i in range(3):
            row_idx = i + 1
            
            # Source
            src = Source(env, id=f"Source_R{row_idx}")
            self.sources.append(src)
            
            # Welding Cell
            cell = Welding_Cell(env, id=f"WeldingCell_R{row_idx}")
            self.cells.append(cell)
            
            # Sink
            sink = Sink(env, id=f"SINK_R{row_idx}")
            self.sinks.append(sink)
            
            # Input Buffer
            buf = Buffer(env, id=f"B_src_R{row_idx}")
            self.input_buffers.append(buf)
            
        self.add_child_node(self.sources)
        self.add_child_node(self.cells)
        self.add_child_node(self.sinks)
        self.add_child_edge(self.input_buffers)
        
        # Connections
        for i in range(3):
            # Source -> B_src -> Machine (inside Cell)
            self.input_buffers[i].connect(self.sources[i], self.cells[i].machine)
            
            # Machine (inside Cell) -> Buffer_W (inside Cell) -> Sink
            self.cells[i].buffer.connect(self.cells[i].machine, self.sinks[i])

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