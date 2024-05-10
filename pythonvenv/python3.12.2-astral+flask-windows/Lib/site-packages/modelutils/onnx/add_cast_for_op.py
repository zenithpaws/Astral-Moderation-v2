import argparse
import os
import onnx
import onnx.numpy_helper


def insert_cast_op(model, index, input_name, output_name, to_type):
    node_list = list(model.graph.node)
    cast_node = onnx.helper.make_node('Cast', [input_name], [output_name], to=getattr(onnx.TensorProto, to_type))
    node_list.insert(index, cast_node)

    del model.graph.node[:]
    model.graph.node.extend(node_list)

    print(f"Inserted Cast {input_name} => {output_name}")


def add_cast_for_op(model, index, input_indices, to_type):
    for i in input_indices:
        node = model.graph.node[index]
        input_name = node.input[i]
        new_input_name = input_name + '_' + to_type.lower()
        node.input[i] = new_input_name

        insert_cast_op(model, index, input_name, new_input_name, to_type)
        index += 1


def add_cast(input_filename, output_filename, op_type, input_indices, to_type):
    if os.path.exists(output_filename):
        raise RuntimeError(f"{output_filename} already exists.")

    model = onnx.load(input_filename)

    done = False
    processed_nodes = []
    while not done:
        for i, node in enumerate(model.graph.node):
            if node.op_type == op_type and node.output not in processed_nodes:
                add_cast_for_op(model, i, input_indices, to_type)
                print(f"Added casts for name: {node.name}, op_type: {node.op_type}")
                processed_nodes.append(node.output)
                continue
        done = True

    onnx.checker.check_model(model)
    onnx.save(model, output_filename)


def main():
    parser = argparse.ArgumentParser("Add Cast operators to the inputs of specified op")
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)
    parser.add_argument('--op_type', type=str, default='NonMaxSuppression', help="Operator type")
    parser.add_argument('--input_indices', type=str, nargs='+', default=[0, 1, 3, 4], help="input indices")
    parser.add_argument('--to', type=str, default='FLOAT', help="The data type to which the tensors are cast")

    args = parser.parse_args()

    add_cast(args.input_filepath, args.output_filepath, args.op_type, args.input_indices, args.to)


if __name__ == '__main__':
    main()
