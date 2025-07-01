
def connect_chain(env, count, node_cls, edge_cls,
                  node_kwargs=None, edge_kwargs=None,
                  node_kwargs_list=None, edge_kwargs_list=None,
                  prefix="Node", edge_prefix="Edge"):
    nodes = []
    edges = []
    
    for i in range(count):
        if node_kwargs_list:
            kwargs = node_kwargs_list[i].copy()
        elif node_kwargs is not None:
            kwargs = node_kwargs.copy()
        else:
            kwargs = {"processing_delay": 0.8, "blocking": True}.copy()

        node_name = f"{prefix}_{i + 1}"
        if "id" in kwargs:
            node_name = kwargs.pop("id")

        print(f"Creating node {node_name} with kwargs: {kwargs}", flush=True)
        node = node_cls(env=env, id=node_name, **kwargs)
        nodes.append(node)

    for i in range(count + 1):
        if edge_kwargs_list:
            kwargs = edge_kwargs_list[i].copy()
        elif edge_kwargs is not None:
            kwargs = edge_kwargs.copy()
        else:
            kwargs = {"delay": 0}.copy()

        edge_name = f"{edge_prefix}_{i + 1}"
        if "id" in kwargs:
            edge_name = kwargs.pop("id")

        edge = edge_cls(env=env, id=edge_name, **kwargs)
        edges.append(edge)

    return nodes, edges


def connect_chain_with_source_sink(env, count, node_cls, edge_cls,
                                    node_kwargs=None, edge_kwargs=None,
                                    node_kwargs_list=None, edge_kwargs_list=None,
                                    prefix="Node", edge_prefix="Edge",
                                    source_cls=None, sink_cls=None,
                                    source_kwargs=None, sink_kwargs=None):
    nodes, edges = connect_chain(env, count, node_cls, edge_cls,
                                 node_kwargs, edge_kwargs,
                                 node_kwargs_list, edge_kwargs_list,
                                 prefix, edge_prefix)
    
    if source_cls:
        source_kwargs = source_kwargs if source_kwargs else {"inter_arrival_time": 1, "blocking": True, "out_edge_selection":"ROUND_ROBIN"}.copy()
        src_name = "Source"
        if "id" in source_kwargs:
            src_name = source_kwargs["id"]
            del source_kwargs["id"]
        source = source_cls(env=env, id=src_name, **source_kwargs)
        nodes.insert(0, source)
    else:
        source = None

    if sink_cls:
        sink_kwargs = sink_kwargs if sink_kwargs else {}.copy()
        sink_name = "Sink"
        if "id" in sink_kwargs:
            sink_name = sink_kwargs["id"]
            del sink_kwargs["id"]
        sink = sink_cls(env=env, id=sink_name, **sink_kwargs)
        nodes.append(sink)
    else:
        sink = None

    return nodes, edges, source, sink


def connect_nodes_with_buffers(machines, buffers, src, sink):
    """
    Connects source, machines, buffers, and optionally a sink in the following order:
    src -> buffer1 -> machine1 -> buffer2 -> machine2 -> ... -> bufferN -> sink

    Args:
        src: Source node
        machines: List of machine nodes
        buffers: List of buffer edges (should be len(machines) - 1) including source and sink
        sink: Optional sink node

    Returns:
        List of all nodes and buffers in connection order
    """
    assert len(buffers) == len(machines) - 1, "Number of buffers must be one more than number of machines"

    # Connect intermediate machines and buffers
    for i in range(1, len(machines)):
        buffers[i - 1].connect(machines[i - 1], machines[i])

    return machines, buffers
