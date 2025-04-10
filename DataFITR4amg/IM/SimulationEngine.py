import simpy
import os
import sys

# Add the FactorySimPy/src folder to the Python path
#print("FactorySimPy path:", os.path.abspath('../../FactorySimPy/src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FactorySimPy/src')))

# Verify if the Sink module exists in the specified path
# if not os.path.exists(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../FactorySimPy/src')), 'Monitor.py')):
#     raise ImportError("The module 'Monitor' could not be found in the specified path.")
#print("ho/a",os.path.abspath('../FactorySimPy/src'))


from Monitor import SystemMonitor, ProcessorMonitor
from Source import Source
from Sink import Sink
from Processor import Processor
from Buffer import Buffer


def simulation_engine(comp_dict, comp_graph):
    """Simulation engine with explicit node and edge handling"""
    env = simpy.Environment()
    system_monitor = SystemMonitor()


    nodes = {}
    edges = {}

    # Initialize Nodes and Edges
    for node_id, details in comp_dict.items():
        if details['type'] in ['Source', 'Sink', 'Processor', 'Machine']:
            if details['type'] == 'Source':
                print(f"Time = {env.now:.2f} Initialised a source {node_id}")
                #system_monitor.register_processor(nodes[node_id])
                nodes[node_id] = Source(env, node_id, 1, 10, 1)

            elif details['type'] == 'Sink':
                print(f"Time = {env.now:.2f} Initialised a sink {node_id}")
                nodes[node_id] = Sink(env, node_id, [], 1, 10, 1)
            elif details['type'] in [ 'Processor' , 'Machine']:
                print(f"Time = {env.now:.2f} Initialised a processor {node_id}")
                nodes[node_id] = Processor(env, node_id, [], [], 2, 2, 1,)
                #print(f"Time = {env.now:.2f} monitor is added to systemmonitor {nodes[node_id].name}")
                system_monitor.register_processor(nodes[node_id])

        elif details['type'] == 'Buffer':
            print(f"Time = {env.now:.2f} Initialised an Buffer {node_id}")
            edges[node_id] = Buffer(env, node_id)

    # Establish Connections
    for source, target in comp_graph.edges():
        print(f"Time = {env.now:.2f} Connecting {source} to {target}")
        if source in nodes and target in nodes:

            if isinstance(nodes[source], Source):
                nodes[source].add_out_edges(nodes[target])
            elif hasattr(nodes[source], 'out_edges'):
                nodes[source].add_out_edges(nodes[target])

            if hasattr(nodes[target], 'in_edges'):
                nodes[target].add_in_edges(nodes[source])

        elif source in edges and target in nodes:
            print(f"Time = {env.now:.2f} Connecting1 {source}--{edges[source].name} to {target}--{nodes[target].name}")

            nodes[target].add_in_edges(edges[source])

            edges[source].dest_node=edges[source]
            #print(f"Time = {env.now:.2f} Connecting11 {source}--{nodes[source].in_edges} ")
        elif source in nodes and target in edges:
            print(f"Time = {env.now:.2f} Connecting2 {source}--{nodes[source].name} to {target}--{edges[target].name}")
            nodes[source].add_out_edges(edges[target])
            edges[target].src_node=nodes[source]
            #print(f"Time = {env.now:.2f} Connecting22 {source}--{nodes[source].out_edges} ")


    # print("\n--- Node Connections ---")
    # print(nodes)
    # for i in nodes:
        
    #     print(f"{i} outconnections: {[edge.name for edge in nodes[i].out_edges]}")
    #     print(f"{i} inconnections: {[edge.name for edge in nodes[i].in_edges]}")
    # Run simulation
    env.run(until=10)

    
    
    print("\n--- Processor Summaries ---")
    for name, data in system_monitor.summary().items():
        print(f"{name}: {data}")

    return system_monitor.summary()