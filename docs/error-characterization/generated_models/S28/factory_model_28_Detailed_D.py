"""
ModelDescription:
"A hierarchical subsystem Cell_X consists of two machines in series with a buffer in between. Three instances of Cell_X are connected in series:

Cell_X_1 has delays (2.0, 2.0)
Cell_X_2 has delays (2.5, 2.0)
Cell_X_3 has delays (3.0, 2.5)
Name machines as M1,M2,.. and buffers as B1,B2,..
All buffers have capacity 2.Single Source(2.1) and Sink."  ALL buffers to be named as ID= B1,B2, etc.

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

class Cell_X(Node):
    def __init__(self, env, id, delays):
        super().__init__(env, id)
        
        # Creating machines M1 and M2
        self.M1 = Machine(env, id="M1", processing_delay=delays[0])
        self.M2 = Machine(env, id="M2", processing_delay=delays[1])
        self.add_child_node([self.M1, self.M2])
        
        # Creating buffer B1 between machines
        self.B1 = Buffer(env, id="B1", capacity=2)
        self.add_child_edge(self.B1)
        
        # Connecting M1 -> B1 -> M2
        self.B1.connect(self.M1, self.M2)
        
        # Exposing endpoints
        self.entry = self.M1
        self.exit = self.M2

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Initializing source
        self.source = Source(env, id="src", inter_arrival_time=2.1)
        self.add_child_node(self.source)
        
        # Initializing sink
        self.sink = Sink(env, id="sink")
        self.add_child_node(self.sink)
        
        # Creating 3 instances of Cell_X with specific delays
        cell_delays = [(2.0, 2.0), (2.5, 2.0), (3.0, 2.5)]
        self.cells = []
        for i, delays in enumerate(cell_delays):
            cell = Cell_X(env, id=f"Cell_X_{i+1}", delays=delays)
            self.cells.append(cell)
        self.add_child_node(self.cells)
        
        # Creating buffers to connect Source -> Cells -> Sink
        # We need 4 buffers: Src->C1, C1->C2, C2->C3, C3->Sink
        self.buffers = [Buffer(env, id=f"B{i+1}", capacity=2) for i in range(4)]
        self.add_child_edge(self.buffers)
        
        # Connecting Source to first Cell
        self.buffers[0].connect(self.source, self.cells[0].entry)
        
        # Connecting Cells in series
        for i in range(2):
            self.buffers[i+1].connect(self.cells[i].exit, self.cells[i+1].entry)
            
        # Connecting last Cell to Sink
        self.buffers[3].connect(self.cells[-1].exit, self.sink)

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