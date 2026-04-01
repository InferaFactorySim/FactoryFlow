"""
ModelDescription:
A system with 4 machines in series.An output of M2 output goes back to M1. An output of M4 output goes back to M1. .

 MODEL ASSUMPTIONS:
1. Node names (M1, M2, M4) are chosen according to the user's description, and M3 is inferred to complete the set of 4 machines.
2. Added a Source node ('SRC') to feed the first machine (M1) and a Sink node ('SINK') to receive output from the last machine (M4) to complete the system flow.Machine IDs are M1, M2, M3, M4,
3. Used 'Buffer' as the default edge type for all connections.bUFFER IDs are B_srcnodeID_destinationnodeID. eg. B_SRC_M1, B_M1_M2,..
4. Used a single buffer for every connection between nodes.
5. Inferred a linear forward flow sequence: Source -> M1 -> M2 -> M3 -> M4 -> Sink.
6. Inferred feedback connections M2 -> M1 and M4 -> M1 as specified.
7. Used default values for all missing parameters (processing delays, inter-arrival times, buffer capacities) for all components.
8. Assumed standard routing logic for machines with multiple outputs (M2 and M4) as no specific split ratios were provided.
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

        # Initializing source
        self.source = Source(env, id='SRC')
        self.add_child_node(self.source)

        # Initializing machines M1 to M4
        self.machines = [Machine(env, id=f'M{i+1}') for i in range(4)]
        self.add_child_node(self.machines)

        # Initializing sink
        self.sink = Sink(env, id='SINK')
        self.add_child_node(self.sink)

        # Defining connections
        # Format: (source_node, destination_node, source_id, destination_id)
        connections = []
        
        # Source -> M1
        connections.append((self.source, self.machines[0], 'SRC', 'M1'))
        
        # Linear sequence M1 -> M2 -> M3 -> M4
        for i in range(3):
            connections.append((self.machines[i], self.machines[i+1], f'M{i+1}', f'M{i+2}'))
            
        # M4 -> Sink
        connections.append((self.machines[3], self.sink, 'M4', 'SINK'))
        
        # Feedback M2 -> M1
        connections.append((self.machines[1], self.machines[0], 'M2', 'M1'))
        
        # Feedback M4 -> M1
        connections.append((self.machines[3], self.machines[0], 'M4', 'M1'))

        # Creating buffers
        self.buffers = []
        for src, dst, src_id, dst_id in connections:
            buf_id = f"B_{src_id}_{dst_id}"
            self.buffers.append(Buffer(env, id=buf_id))
            
        # Adding buffers to child edges
        self.add_child_edge(self.buffers)
        
        # Connecting nodes
        for i, (src, dst, _, _) in enumerate(connections):
            self.buffers[i].connect(src, dst)

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