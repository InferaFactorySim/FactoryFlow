"""
ModelDescription:
Parts flow from two machines and merge to one path and enters a  machine. Both sources have delay of 10

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
10. All machines have a processing_Delay of 2 and buffers have a capacity of 2. The work_capacity of machine_M3 is 2.
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

        # Creating nodes based on assumptions
        self.Source_1 = Source(env, id="Source_1", inter_arrival_time=10)
        self.Source_2 = Source(env, id="Source_2", inter_arrival_time=10)
        
        # Machines with processing_delay=2 as per assumption 10
        self.Machine_M1 = Machine(env, id="Machine_M1", processing_delay=2)
        self.Machine_M2 = Machine(env, id="Machine_M2", processing_delay=2)
        # Machine M3 with work_capacity=2 as per assumption 10
        self.Machine_M3 = Machine(env, id="Machine_M3", processing_delay=2, work_capacity=2)
        
        self.Sink = Sink(env, id="Sink")

        # Adding nodes to child nodes
        self.add_child_node([self.Source_1, self.Source_2, self.Machine_M1, self.Machine_M2, self.Machine_M3, self.Sink])
        
        # Defining source and sink attributes
        self.sources = [self.Source_1, self.Source_2]
        self.sink = self.Sink

        # Creating edges with capacity=2 as per assumption 10 and IDs from assumption 4
        self.Buffer_src1 = Buffer(env, id="Buffer_src1", capacity=2)
        self.Buffer_src2 = Buffer(env, id="Buffer_src2", capacity=2)
        self.Buffer_Join1 = Buffer(env, id="Buffer_Join1", capacity=2)
        self.Buffer_Join2 = Buffer(env, id="Buffer_Join2", capacity=2)
        self.Buffer_main_sink = Buffer(env, id="Buffer_main_sink", capacity=2)

        # Adding edges to child edges
        self.add_child_edge([self.Buffer_src1, self.Buffer_src2, self.Buffer_Join1, self.Buffer_Join2, self.Buffer_main_sink])

        # Connecting nodes
        # Source 1 -> M1
        self.Buffer_src1.connect(self.Source_1, self.Machine_M1)
        # Source 2 -> M2
        self.Buffer_src2.connect(self.Source_2, self.Machine_M2)
        # M1 -> M3
        self.Buffer_Join1.connect(self.Machine_M1, self.Machine_M3)
        # M2 -> M3
        self.Buffer_Join2.connect(self.Machine_M2, self.Machine_M3)
        # M3 -> Sink
        self.Buffer_main_sink.connect(self.Machine_M3, self.Sink)

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