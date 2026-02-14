"""
ModelDescription:
Parts flow from two machines and merge to one path and enters a  machine

 MODEL ASSUMPTIONS:
1. Inferred node names: `Source_1` and 'Source_2 for the input, `Machine_M1` and `Machine_M2` for the two initial machines, `Machine_M3` for the final machine, and `Sink` for the output.
2. Added `Source` and `Sink` nodes to complete the simulation flow as they were not specified.
3. Used `Machine` node type for all processing units.
4. Used `Buffer` edge type for all connections and IDs are Buffer_src1, Buffer_src2, Buffer_Join1, Buffer_Join2 and Buffer_main_sink
5. Assumed the `Source` connects to both `M1` and `M2` to initiate the flow.
6. Assumed `M1` and `M2` both connect to `M3` to represent the merging of paths into the final machine.
7. Assumed `M3` connects to `Sink`.
8. Used a single buffer for each connection between nodes.
9. Used default values for all missing parameters (processing delays, inter-arrival times, capacities).
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

        # Creating Sources based on Assumption 1: Source_1 and Source_2
        self.sources = [Source(env, id=f"Source_{i+1}") for i in range(2)]
        self.add_child_node(self.sources)

        # Creating Machines based on Assumption 1
        # Machine_M1 and Machine_M2 are the two initial machines
        self.machines_start = [Machine(env, id=f"Machine_M{i+1}") for i in range(2)]
        self.add_child_node(self.machines_start)
        
        # Machine_M3 is the final machine
        self.machine_end = Machine(env, id="Machine_M3")
        self.add_child_node(self.machine_end)

        # Creating Sink based on Assumption 1
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)

        # Creating Edges based on Assumption 4
        # Buffers connecting Sources to Start Machines: Buffer_src1, Buffer_src2
        self.buffer_src = [Buffer(env, id=f"Buffer_src{i+1}") for i in range(2)]
        self.add_child_edge(self.buffer_src)

        # Buffers connecting Start Machines to End Machine: Buffer_Join1, Buffer_Join2
        self.buffer_join = [Buffer(env, id=f"Buffer_Join{i+1}") for i in range(2)]
        self.add_child_edge(self.buffer_join)

        # Buffer connecting End Machine to Sink: Buffer_main_sink
        self.buffer_sink = Buffer(env, id="Buffer_main_sink")
        self.add_child_edge(self.buffer_sink)

        # Connecting Nodes
        for i in range(2):
            # Connect Source_i to Machine_Mi
            self.buffer_src[i].connect(self.sources[i], self.machines_start[i])
            # Connect Machine_Mi to Machine_M3 (Merge)
            self.buffer_join[i].connect(self.machines_start[i], self.machine_end)
        
        # Connect Machine_M3 to Sink
        self.buffer_sink.connect(self.machine_end, self.sink)

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