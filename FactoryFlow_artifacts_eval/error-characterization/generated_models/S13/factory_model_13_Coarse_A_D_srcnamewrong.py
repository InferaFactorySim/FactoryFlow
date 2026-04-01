"""
ModelDescription:
A linear sequence of 3 machines each with a delay of 4,3,2 connected with a sink and a source. 4 such sequences are in parallel. There is a connection between the M1 in r1 and M1 in row2 and a connection between M3 in row2 and M3 in row4. Source `SRC` with delay 2.5. Buffers with capacity=2

 MODEL ASSUMPTIONS:
1. A class named `LinearSequence` is created to represent the repeated pattern of "A linear sequence of 3 machines... connected with a sink and a source".
2. A repeated pattern class named `Stage` is inferred, consisting of one Machine (`Stage_i_M1`) followed by one Buffer (`Stage_i_B1`).
3. A repeated pattern class named `Sequence` (or `Row`) is inferred, consisting of 3 sequential `Stage` subsystems.
4. The specific processing delays (4.0, 3, 2) and capacities (2, 3, 4) specified for the three stages are used, overriding the later generic statement "All machines have a processing_Delay of 2 and buffers have a capacity of 2", which is assumed to apply only to components where specific values were not provided (like cross-buffers).
5. The single buffer `B_src_1` connects the Source `SRC`  to the first machine (`Stage_1_M1`) . Every sequence has a separate SRC and a S_src_1
6. The output buffer of the last stage (`Stage_3_B1`) in all 4 parallel sequences connects to the separate Sinks `SINK`.
7. Cross-connections are assumed to flow from the lower row index to the higher row index (Row 1 to Row 2, and Row 2 to Row 4).
8. The reference to "M3" in the cross-connection description is assumed to refer to the Machine located in Stage 3 (`Stage_3_M1`).
9. `Cross_Buffer_1` connects Row 1's Stage 1 Machine to Row 2's Stage 1 Machine.
10. `Cross_Buffer_2` connects Row 2's Stage 3 Machine to Row 4's Stage 3 Machine.
6. The connection "between M1 in r1 and M1 in row2" is assumed to be a directed flow from `Row1.M1` to `Row2.M1`.
7. The connection "between M3 in row2 and M3 in row4" is assumed to be a directed flow from `Row2.M3` to `Row4.M3`.
8. Used default values for all missing parameters (e.g., source inter-arrival times, buffer capacities) for all components.
"""

import simpy
import factorysimpy
from factorysimpy.nodes.node import Node
from factorysimpy.nodes.machine import Machine
from factorysimpy.edges.buffer import Buffer
from factorysimpy.nodes.source import Source
from factorysimpy.nodes.sink import Sink

class Stage(Node):
    def __init__(self, env, id, delay, capacity):
        super().__init__(env, id)
        # Assumption 2: Stage consists of one Machine (Stage_i_M1) followed by one Buffer (Stage_i_B1)
        self.M1 = Machine(env, id=f"{id}_M1", processing_delay=delay)
        self.add_child_node(self.M1)
        
        self.B1 = Buffer(env, id=f"{id}_B1", capacity=capacity)
        self.add_child_edge(self.B1)

class LinearSequence(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Assumption 5: Every sequence has a separate SRC
        # Description: Source SRC with delay 2.5 (interpreted as inter_arrival_time)
        self.source = Source(env, id=f"{id}_SRC", inter_arrival_time=2.5)
        self.add_child_node(self.source)
        
        # Assumption 6: Separate Sinks SINK
        self.sink = Sink(env, id=f"{id}_SINK")
        self.add_child_node(self.sink)
        
        # Assumption 4: Specific processing delays (4.0, 3, 2) and capacities (2, 3, 4)
        delays = [4.0, 3.0, 2.0]
        capacities = [2, 3, 4]
        
        # Assumption 3: Sequence consists of 3 sequential Stage subsystems
        self.stages = []
        for i in range(3):
            stage = Stage(env, id=f"{id}_Stage_{i+1}", delay=delays[i], capacity=capacities[i])
            self.stages.append(stage)
        self.add_child_node(self.stages)
        
        # Assumption 5: B_src_1 connects SRC to Stage 1
        self.B_src_1 = Buffer(env, id=f"{id}_B_src_1", capacity=2)
        self.add_child_edge(self.B_src_1)
        self.B_src_1.connect(self.source, self.stages[0].M1)
        
        # Connect Stages
        # Stage 1 B1 -> Stage 2 M1
        self.stages[0].B1.connect(self.stages[0].M1, self.stages[1].M1)
        # Stage 2 B1 -> Stage 3 M1
        self.stages[1].B1.connect(self.stages[1].M1, self.stages[2].M1)
        
        # Assumption 6: Output buffer of last stage connects to SINK
        self.stages[2].B1.connect(self.stages[2].M1, self.sink)

class SystemModel(Node):
    def __init__(self, env, id):
        super().__init__(env, id)
        
        # Description: 4 such sequences are in parallel
        self.rows = [LinearSequence(env, id=f"Row{i+1}") for i in range(4)]
        self.add_child_node(self.rows)
        
        # Assumption 9: Cross_Buffer_1 connects Row 1's Stage 1 Machine to Row 2's Stage 1 Machine
        self.Cross_Buffer_1 = Buffer(env, id="Cross_Buffer_1", capacity=2)
        self.add_child_edge(self.Cross_Buffer_1)
        # Row 1 is index 0, Row 2 is index 1
        self.Cross_Buffer_1.connect(self.rows[0].stages[0].M1, self.rows[1].stages[0].M1)
        
        # Assumption 10: Cross_Buffer_2 connects Row 2's Stage 3 Machine to Row 4's Stage 3 Machine
        self.Cross_Buffer_2 = Buffer(env, id="Cross_Buffer_2", capacity=2)
        self.add_child_edge(self.Cross_Buffer_2)
        # Row 2 is index 1, Row 4 is index 3
        # Stage 3 is index 2
        self.Cross_Buffer_2.connect(self.rows[1].stages[2].M1, self.rows[3].stages[2].M1)

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