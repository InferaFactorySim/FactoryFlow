"""
ModelDescription:
A system composed of a repeated hierarchical subsystem, where each subsystem contains two machines in series connected by a buffer.  Three such subsystems are connected sequentially, forming a linear hierarchical structure with a single source and a single sink. The subsystems are heterogeneous. All buffer ID are Bi, i=1,2,3 if buffer ID is not available.

Cell_X_1 has delays (2.0, 2.0)
Cell_X_2 has delays (2.5, 2.0)
Cell_X_3 has delays (3.0, 2.5)

All buffers have capacity 2.Single Source(2.1) 

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to user's description.
2. Inferred a class named `Subsystem` for the repeated hierarchical pattern containing two machines in series.
3. Inferred machine IDs within the `Subsystem` as `M1` and `M2` via 'B1'
4. Inferred top-level system class name as `SystemModel`.
5. Used default edge type `Buffer` for all connections where edge type was not specified (specifically between the sequential subsystems and connecting the source/sink).
6. Used a single buffer for all connections between nodes and subsystems where the number of buffers was not specified.
7. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
8. Inferred logical flow: Source -> B1 -> Cell_X_1 -> B2 -> Cell_X_2 -> B3 -> Cell_X_3 -> B4 -> sink.
9. Inferred logical flow within `Subsystem`: `M1` -> B1 -> `M2`.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the repeated hierarchical subsystem
class Subsystem(Node):
    def __init__(self, env, id, delays):
        super().__init__(env, id)
        
        # Creating machines M1 and M2 with specified delays
        self.M1 = Machine(env, id="M1", processing_delay=delays[0])
        self.M2 = Machine(env, id="M2", processing_delay=delays[1])
        self.add_child_node([self.M1, self.M2])
        
        # Creating internal buffer B1 with capacity 2
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        # Connecting M1 -> B1 -> M2
        self.B1.connect(self.M1, self.M2)

# Defining the top-level system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Creating Source with inter_arrival_time 2.1
        self.source = Source(env, id="src", inter_arrival_time=2.1)
        self.add_child_node(self.source)
        
        # Defining subsystem parameters
        cell_params = [
            ("Cell_X_1", (2.0, 2.0)),
            ("Cell_X_2", (2.5, 2.0)),
            ("Cell_X_3", (3.0, 2.5))
        ]
        
        # Creating subsystems
        self.cells = []
        for name, delays in cell_params:
            cell = Subsystem(env, id=name, delays=delays)
            self.cells.append(cell)
        self.add_child_node(self.cells)
        
        # Creating Sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating connecting buffers B1, B2, B3, B4 with capacity 2
        self.buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.buffers)
        
        # Connecting Source -> B1 -> Cell_X_1 (M1)
        self.buffers[0].connect(self.source, self.cells[0].M1)
        
        # Connecting Cell_X_i (M2) -> B(i+2) -> Cell_X_i+1 (M1)
        for i in range(2):
            self.buffers[i+1].connect(self.cells[i].M2, self.cells[i+1].M1)
            
        # Connecting Cell_X_3 (M2) -> B4 -> Sink
        self.buffers[3].connect(self.cells[2].M2, self.sink)

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