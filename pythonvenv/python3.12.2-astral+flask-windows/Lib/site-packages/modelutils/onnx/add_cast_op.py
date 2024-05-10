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


def add_cast_to_tensor(model, tensor_name, to_type):
    for index, node in enumerate(model.graph.node):
        for i, output in enumerate(node.output):
            if output == tensor_name:
                insert_cast_op(model, index + 1, tensor_name, tensor_name + '_' + to_type.lower(), to_type)
                return model

    raise RuntimeError(f"tensor name {tensor_name} is not found")


def add_cast(input_filename, output_filename, tensor_names, to_type):
    if os.path.exists(output_filename):
        raise RuntimeError(f"{output_filename} already exists.")

    model = onnx.load(input_filename)

    for tensor_name in tensor_names:
        add_cast_to_tensor(model, tensor_name, to_type)

    onnx.checker.check_model(model)
    onnx.save(model, output_filename)


def main():
    parser = argparse.ArgumentParser("Add Cast operators to the specified tensors")
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)
    parser.add_argument('--tensor_name', type=str, nargs='+', default=[], help="Tensor names to be cast")
    parser.add_argument('--to', type=str, default='FLOAT', help="The data type to which the tensors are cast")

    args = parser.parse_args()

    add_cast(args.input_filepath, args.output_filepath, args.tensor_name, args.to)


if __name__ == '__main__':
    main()
