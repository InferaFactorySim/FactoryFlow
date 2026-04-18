"""
ModelDescription:
"A hierarchical subsystem Cell_X consists of two machines in series with a buffer in between. Three instances of Cell_X are connected in series:

Cell_X_1 has delays (2.0, 2.0)
Cell_X_2 has delays (2.5, 2.0)
Cell_X_3 has delays (3.0, 2.5)
Name machines as M1,M2,.. and buffers as B1,B2,..
All buffers have capacity 2.Single Source(2.1) and Sink."

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to users description.
2. Inferred a class named `Cell_X` to represent the repeated subsystem pattern consisting of two machines and an internal buffer.
3. Assumed the processing delays provided (e.g., 2.0, 2.0) apply sequentially to the first and second machine within each `Cell_X` instance respectively.
4. Used default edge type `Buffer` for connecting the Source to `Cell_X_1`, `Cell_X_1` to `Cell_X_2`, `Cell_X_2` to `Cell_X_3`, and `Cell_X_3` to the Sink, as specific connection types were not specified.
5. Assumed a single buffer is used for all connections between the subsystems and the source/sink.
6. Assumed the global constraint "All buffers have capacity 2" applies to the inferred buffers connecting the subsystems as well.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

# Defining the hierarchical subsystem Cell_X
class Cell_X(Node):
    def __init__(self, env, id, delays):
        super().__init__(env, id)
        
        # Creating machines M1 and M2 with specified delays
        self.M1 = Machine(env, id="M1", processing_delay=delays[0])
        self.M2 = Machine(env, id="M2", processing_delay=delays[1])
        self.add_child_node([self.M1, self.M2])
        
        # Creating internal buffer B1 with capacity 2
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        # Connecting M1 to M2 via B1
        self.B1.connect(self.M1, self.M2)
        
        # Exposing entry and exit points for the cell
        self.entry = self.M1
        self.exit = self.M2

# Defining the overall system model
class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source with inter_arrival_time 2.1
        self.source = Source(env, id="src", inter_arrival_time=2.1)
        self.add_child_node(self.source)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Configuration for the 3 cells
        cell_configs = [
            (2.0, 2.0), # Cell_X_1
            (2.5, 2.0), # Cell_X_2
            (3.0, 2.5)  # Cell_X_3
        ]
        
        # Creating Cell_X instances
        self.cells = []
        for i, delays in enumerate(cell_configs):
            cell = Cell_X(env, id=f"Cell_X_{i+1}", delays=delays)
            self.cells.append(cell)
        self.add_child_node(self.cells)
        
        # Creating edges to connect Source -> Cells -> Sink
        self.edges = []
        
        # Connect Source to first Cell
        edge_src = Buffer(env, id="edge[0]", capacity=2)
        self.add_child_edge(edge_src)
        edge_src.connect(self.source, self.cells[0].entry)
        self.edges.append(edge_src)
        
        # Connect Cells in series
        for i in range(len(self.cells) - 1):
            edge = Buffer(env, id=f"edge[{i+1}]", capacity=2)
            self.add_child_edge(edge)
            edge.connect(self.cells[i].exit, self.cells[i+1].entry)
            self.edges.append(edge)
            
        # Connect last Cell to Sink
        edge_sink = Buffer(env, id=f"edge[{len(self.cells)}]", capacity=2)
        self.add_child_edge(edge_sink)
        edge_sink.connect(self.cells[-1].exit, self.sink)
        self.edges.append(edge_sink)

# Initializing simpy environment
env = simpy.Environment()

# Creating the system model
TOP = SystemModel(env, "TOP")

# Filling hierarchical ids from TOP
TOP.fill_hierarchical_id()

# Validating the model
TOP.validate()

# Running the simulation
TOP.run_simulation(25)