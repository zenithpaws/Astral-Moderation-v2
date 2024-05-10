import argparse
import os
import onnx
import onnx.shape_inference


def cut_graph(model_filename, output_filename, input_names, output_names):
    """Get a minimum sub graph which has the given input names and the output names.
    Args:
        model_filename: Input model filename.
        output_filename: Output model filename.
        input_names: list of input tensor names. If empty, the model input names are used.
        output_names: list of output tensor names. If empty, the model output names are used.
    """
    if os.path.exists(output_filename):
        raise RuntimeError(f"{output_filename} already exists.")

    model = onnx.load(model_filename)

    if not input_names:
        input_names = set([i.name for i in model.graph.input]) - set([i.name for i in model.graph.initializer])

    if not output_names:
        output_names = [o.name for o in model.graph.output]

    required_nodes = set()
    to_visit_nodes = []
    initializer_nodes = [i.name for i in model.graph.initializer]
    required_initializers = []

    for name in output_names:
        for node in model.graph.node:
            if name in node.output:
                required_nodes.add(name)
                for input in node.input:
                    if input not in to_visit_nodes and input not in required_nodes:
                        to_visit_nodes.append(input)
                break

    while to_visit_nodes:
        next_node_output = to_visit_nodes.pop()
        if next_node_output in initializer_nodes:
            required_initializers.append(next_node_output)
            continue
        required_nodes.add(next_node_output)
        next_node = _get_node_by_output(model.graph.node, next_node_output)
        if not next_node:
            raise RuntimeError(f"node {next_node_output} is not found. Maybe you need to add it to input_names")

        for input in next_node.input:
            if input and input not in to_visit_nodes and input not in required_nodes and input not in input_names:
                to_visit_nodes.append(input)

    # Cut a subgraph.
    nodes_list = list(model.graph.node)
    nodes_list = [node for node in nodes_list if any([o in required_nodes for o in node.output])]
    del model.graph.node[:]
    model.graph.node.extend(nodes_list)

    # Get shapes of the tensors.
    inferred_model = onnx.shape_inference.infer_shapes(model)
    original_value_info = inferred_model.graph.value_info
    original_value_info.extend(model.graph.input)
    original_value_info.extend(model.graph.output)

    # New output descriptions
    del model.graph.output[:]
    for name in output_names:
        value_info = [v for v in original_value_info if v.name == name][0]
        model.graph.output.append(value_info)

    # New input descriptions
    del model.graph.input[:]
    for name in input_names:
        found_value_info = [v for v in original_value_info if v.name == name]
        if not found_value_info:
            # TODO: What is this case? Avoid hard-coding something.
            value_info = onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT, (1, 3, 416, 416))
        else:
            value_info = found_value_info[0]
        model.graph.input.append(value_info)

    # Remove unused initializers
    initializers = list(model.graph.initializer)
    del model.graph.initializer[:]
    initializers = [i for i in initializers if i.name in required_initializers]
    model.graph.initializer.extend(initializers)

    onnx.checker.check_model(model)
    onnx.save(model, output_filename)


def _get_node_by_output(nodes, output_name):
    for node in nodes:
        if output_name in node.output:
            return node
    return None


def main():
    parser = argparse.ArgumentParser("Cut a subgraph from a ONNX model")
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)
    parser.add_argument('--input_names', type=str, nargs='+', default=[], help="The input names for the sub graph.")
    parser.add_argument('--output_names', type=str, nargs='+', default=[], help="The output names for the sub graph.")

    args = parser.parse_args()

    cut_graph(args.input_filepath, args.output_filepath, args.input_names, args.output_names)


if __name__ == '__main__':
    main()
