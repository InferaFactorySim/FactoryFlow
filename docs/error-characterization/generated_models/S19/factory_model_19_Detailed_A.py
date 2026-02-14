"""
ModelDescription:
A source with ID Source(3.3s) feeds a splitter that distributes items to three parallel machines. 
Machine_Alpha has a processing delay of 1.0s. Machine_Beta and Machine_Gamma 
 have processing delays of 10.0 and 20s. All three connect to Sink . All buffers 
 have a capacity of 5. Each machine has its own buffer from the source and to the sink.
 B_src_i connects Source to Machine_i, and B_sink_i connects Machine_i to Sink.

 MODEL ASSUMPTIONS:
1. Node names and Types are chosen according to the user's description.
2. The "splitter" mentioned in the description is assumed to be the Source node itself acting as a distributor, rather than a separate node, because the buffer definitions explicitly state they connect the Source directly to the Machines (`B_src_i` connects `Source` to `Machine_i`).
3. The identifier `i` in the buffer naming conventions (`B_src_i`, `B_sink_i`) is assumed to be replaced by the specific machine name suffixes: 1,2,3
4. Used default values for all missing parameters for all components (such as the routing logic/output edge selection for the Source).
5. Assumed a single buffer is used for each connection path described.
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
        self.source = Source(env, id="Source", inter_arrival_time=3.3)
        self.add_child_node(self.source)

        # initializing sink
        self.sink = Sink(env, id="Sink")
        self.add_child_node(self.sink)

        # Machine configuration: (ID, Processing Delay, Buffer Suffix)
        # Derived from description and assumptions
        machine_config = [
            ("Machine_Alpha", 1.0, 1),
            ("Machine_Beta", 10.0, 2),
            ("Machine_Gamma", 20.0, 3)
        ]

        # initializing machines
        self.machines = []
        for m_id, delay, _ in machine_config:
            self.machines.append(Machine(env, id=m_id, processing_delay=delay))
        self.add_child_node(self.machines)

        # initializing buffers
        self.src_buffers = []
        self.sink_buffers = []
        
        for _, _, suffix in machine_config:
            # Buffer from Source to Machine (B_src_i)
            self.src_buffers.append(Buffer(env, id=f"B_src_{suffix}", capacity=5))
            # Buffer from Machine to Sink (B_sink_i)
            self.sink_buffers.append(Buffer(env, id=f"B_sink_{suffix}", capacity=5))
            
        self.add_child_edge(self.src_buffers)
        self.add_child_edge(self.sink_buffers)

        # connecting nodes
        for i in range(len(self.machines)):
            # Connect Source -> Buffer -> Machine
            self.src_buffers[i].connect(self.source, self.machines[i])
            # Connect Machine -> Buffer -> Sink
            self.sink_buffers[i].connect(self.machines[i], self.sink)

# initializing simpy environment
env = simpy.Environment()
# creating system model
TOP = SystemModel(env, "TOP")
# filling hierarchical ids
TOP.fill_hierarchical_id()
# validating the model
TOP.validate()
# running the simulation
TOP.run_simulation(25)