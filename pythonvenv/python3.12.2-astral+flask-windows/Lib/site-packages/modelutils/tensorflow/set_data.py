def set_data(model_filepath, name, value):
    import tensorflow
    graph_def = tensorflow.compat.v1.GraphDef()
    graph_def.ParseFromString(model_filepath.read_bytes())

    for node in graph_def.node:
        if node.op == 'Const' and node.name == name:
            new_tensor = tensorflow.make_tensor_proto(value)
            node.attr['value'].tensor.CopyFrom(new_tensor)
            return graph_def.SerializeToString()

    return None
