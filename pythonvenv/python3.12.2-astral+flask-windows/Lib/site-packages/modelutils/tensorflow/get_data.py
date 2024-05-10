def get_data(model_filepath, name):
    import tensorflow
    graph_def = tensorflow.compat.v1.GraphDef()
    graph_def.ParseFromString(model_filepath.read_bytes())

    if name:
        for node in graph_def.node:
            if node.op == 'Const' and node.name == name:
                return tensorflow.make_ndarray(node.attr['value'].tensor)

    return {n.name: tensorflow.make_ndarray(n.attr['value'].tensor) for n in graph_def.node if n.op == 'Const'}
