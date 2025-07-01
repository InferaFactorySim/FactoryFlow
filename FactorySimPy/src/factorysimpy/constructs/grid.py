def connect_2d_grid(env, count, node_cls, edge_cls,
                    node_kwargs=None, edge_kwargs=None,
                    node_kwargs_grid=None, edge_kwargs_grid=None,
                    prefix="Node", edge_prefix="Edge"):
    """
    Creates a 2D grid of machines (count x count), each row is an independent chain.
    Returns:
        nodes_grid: List of lists of nodes (rows)
        edges_grid: List of lists of edges (rows)
    """
    nodes_grid = []
    edges_grid = []

    for row in range(count):
        nodes = []
        edges = []
        for col in range(count):
            # Get kwargs for this node
            if node_kwargs_grid:
                kwargs = node_kwargs_grid[row][col].copy()
            elif node_kwargs is not None:
                kwargs = node_kwargs.copy()
            else:
                kwargs = {"processing_delay": 0.8, "blocking": True}.copy()
            node_name = f"{prefix}_{row+1}_{col+1}"
            if "id" in kwargs:
                node_name = kwargs.pop("id")
            node = node_cls(env=env, id=node_name, **kwargs)
            nodes.append(node)
        for col in range(count + 1):
            # Get kwargs for this edge
            if edge_kwargs_grid:
                kwargs = edge_kwargs_grid[row][col].copy()
            elif edge_kwargs is not None:
                kwargs = edge_kwargs.copy()
            else:
                kwargs = {"delay": 0}.copy()
            edge_name = f"{edge_prefix}_{row+1}_{col+1}"
            if "id" in kwargs:
                edge_name = kwargs.pop("id")
            edge = edge_cls(env=env, id=edge_name, **kwargs)
            edges.append(edge)
        nodes_grid.append(nodes)
        edges_grid.append(edges)
    return nodes_grid, edges_grid


def connect_2d_grid_with_source_sink(
    env, count, node_cls, edge_cls,
    node_kwargs=None, edge_kwargs=None,
    node_kwargs_grid=None, edge_kwargs_grid=None,
    prefix="Node", edge_prefix="Edge",
    source_cls=None, sink_cls=None,
    source_kwargs=None, sink_kwargs=None,
    buffer_cls=None, buffer_kwargs=None
):
    """
    Creates a 2D grid of machines (count x count), each row is an independent chain.
    Adds one source and one sink, each connected via buffers to all first/last machines in each row.
    Returns:
        nodes_grid, edges_grid, source, sink, source_buffers, sink_buffers
    """
    nodes_grid = []
    edges_grid = []

    for row in range(count):
        nodes = []
        edges = []
        for col in range(count):
            if node_kwargs_grid:
                print(f"{row}-{col}")
                kwargs = node_kwargs_grid[row][col].copy()
                print(f"{row}-{col}-{kwargs}")
            elif node_kwargs is not None:
                
                kwargs = node_kwargs.copy()
            else:
                kwargs = {"processing_delay": 0.8, "blocking": True}.copy()
            node_name = f"{prefix}_{row+1}_{col+1}"
            if "id" in kwargs:
                node_name = kwargs.pop("id")
            node = node_cls(env=env, id=node_name, **kwargs)
            nodes.append(node)
        for col in range(count - 1):
            if edge_kwargs_grid:
                kwargs = edge_kwargs_grid[row][col].copy()
            elif edge_kwargs is not None:
                kwargs = edge_kwargs.copy()
            else:
                kwargs = {"delay": 0}.copy()
            edge_name = f"{edge_prefix}_{row+1}_{col+1}"
            if "id" in kwargs:
                edge_name = kwargs.pop("id")
            edge = edge_cls(env=env, id=edge_name, **kwargs)
            edges.append(edge)
        nodes_grid.append(nodes)
        edges_grid.append(edges)

    # --- Connect machines in each row using edges in that row ---
    for row in range(count):
        for col in range(count - 1):
            # Connect edge from nodes_grid[row][col] to nodes_grid[row][col+1]
            edges_grid[row][col].connect(nodes_grid[row][col], nodes_grid[row][col+1])

    # Create source and buffers to first machine in each row
    source = source_cls(env=env, id="Source", **(source_kwargs or {"inter_arrival_time":0.5, "out_edge_selection":"ROUND_ROBIN"}))
    source_buffers = []
    for row in range(count):
        buf = buffer_cls(env=env, id=f"SourceBuffer_{row+1}", **(buffer_kwargs or {}))
        buf.connect(source, nodes_grid[row][0])
        source_buffers.append(buf)

    # Create sink and buffers from last machine in each row
    sink = sink_cls(env=env, id="Sink", **(sink_kwargs or {}))
    sink_buffers = []
    for row in range(count):
        buf = buffer_cls(env=env, id=f"SinkBuffer_{row+1}", **(buffer_kwargs or {}))
        buf.connect(nodes_grid[row][-1], sink)
        sink_buffers.append(buf)

    return nodes_grid, edges_grid, source, sink, source_buffers, sink_buffers

