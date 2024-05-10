def _get_graph_inputs_outputs(graph_def):
    input_names = []
    inputs_set = set()
    outputs_set = set()

    for node in graph_def.node:
        if node.op == 'Placeholder':
            input_names.append(node.name)

        for i in node.input:
            inputs_set.add(i.split(':')[0])
        outputs_set.add(node.name)

    output_names = list(outputs_set - inputs_set)
    return input_names, output_names


def run_model(model_filepath, input_array, output_names):
    import tensorflow
    graph_def = tensorflow.compat.v1.GraphDef()
    graph_def.ParseFromString(model_filepath.read_bytes())

    graph_in, graph_out = _get_graph_inputs_outputs(graph_def)
    output_names = output_names or [o + ':0' for o in graph_out]
    input_tensor_name = graph_in[0] + ':0'

    with tensorflow.compat.v1.Session() as sess:
        tensorflow.import_graph_def(graph_def, name='')
        output_tensors = [sess.graph.get_tensor_by_name(o) for o in output_names]
        outputs = sess.run(output_tensors, {input_tensor_name: input_array})

    return {n: outputs[i] for i, n in enumerate(output_names)}
