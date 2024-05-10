import argparse
import os
import onnx


def insert_cast_op(model, input_name, output_name, to_type, index):
    cast_node = onnx.helper.make_node('Cast', [input_name], [output_name], to=to_type)
    print(f"Added a Cast node: {input_name} => {output_name}")
    nodes_list = list(model.graph.node)
    nodes_list.insert(index, cast_node)
    del model.graph.node[:]
    model.graph.node.extend(nodes_list)


def get_output_node_index(model, name):
    for i, node in enumerate(model.graph.node):
        if name in node.output:
            return i
    return None


def replace_node_input(model, target_nodes, original_input, new_input):
    for node in model.graph.node:
        if node in target_nodes:
            for i, n in enumerate(node.input):
                if n == original_input:
                    node.input[i] = new_input
                    print(f"Update {node.name}. input[{i}]: {n} => {new_input}")
                    return True
    return False


def _merge_model(model, model2):
    model.graph.node.extend(model2.graph.node)
    model.graph.output.extend(model2.graph.output)
    model.graph.initializer.extend(model2.graph.initializer)

    for input in model2.graph.input:
        prev_output = [o for o in model.graph.output if o.name == input.name]
        if prev_output:
            if prev_output[0].type.tensor_type.elem_type != input.type.tensor_type.elem_type:
                # Type is different. Need to insert cast op.
                index = get_output_node_index(model, input.name)
                new_name = input.name + '_' + str(input.type.tensor_type.elem_type)
                insert_cast_op(model, input.name, new_name, input.type.tensor_type.elem_type, index+1)

                target_nodes = [node for node in model2.graph.node if input.name in node.input]
                replace_node_input(model, target_nodes, input.name, new_name)

            # Remove output node and input node
            outputs = list(model.graph.output)
            outputs = [o for o in outputs if o.name != input.name]
            del model.graph.output[:]
            model.graph.output.extend(outputs)

        prev_input = [i for i in model.graph.input if i.name == input.name]
        if prev_input:
            if prev_input[0].type.tensor_type.elem_type != input.type.tensor_type.elem_type:
                new_name = input.name + '_' + str(input.type.tensor_type.elem_type)
                insert_cast_op(model, input.name, new_name, input.type.tensor_type.elem_type, 0)
                target_nodes = [node for node in model2.graph.node if input.name in node.input]
                replace_node_input(model, target_nodes, input.name, new_name)

        if not prev_output and not prev_input:
            model.graph.input.append(input)

    return model


def cat_graph(input_filenames, output_filename):
    if os.path.exists(output_filename):
        raise RuntimeError(f"{output_filename} already exists.")

    models = [onnx.load(filename) for filename in input_filenames]

    for model in models[1:]:
        models[0] = _merge_model(models[0], model)

    onnx.checker.check_model(models[0])
    onnx.save(models[0], output_filename)


def main():
    parser = argparse.ArgumentParser("Concatenate given models")
    parser.add_argument('input_filepath', type=str, nargs='+')
    parser.add_argument('--output_filepath', type=str)

    args = parser.parse_args()

    cat_graph(args.input_filepath, args.output_filepath)


if __name__ == '__main__':
    main()
