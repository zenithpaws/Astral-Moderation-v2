import argparse
import pathlib
import numpy as np
import tensorflow


def update_const(model_filepath, tensor_name, new_value, output_filepath):
    graph_def = tensorflow.compat.v1.GraphDef()
    graph_def.ParseFromString(model_filepath.read_bytes())

    old_value = None
    const_node = None
    for node in graph_def.node:
        if node.op == 'Const' and node.name == tensor_name:
            const_node = node
            break

    assert const_node is not None

    old_value = tensorflow.make_ndarray(const_node.attr['value'].tensor)
    print(f"Old values are: {old_value}")

    if new_value:
        new_value = [float(i) for i in new_value]  # TODO: Is this really float value?
        new_np_array = np.array(new_value, dtype=old_value.dtype).reshape(old_value.shape)
        print(f"New values are: {new_np_array}")

        new_tensor = tensorflow.make_tensor_proto(new_np_array)
        const_node.attr['value'].tensor.CopyFrom(new_tensor)

        if output_filepath:
            output_filepath.write_bytes(graph_def.SerializeToString())
            print(f"Saved to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Update a const value in TensorFlow model")
    parser.add_argument('model_filepath', type=pathlib.Path)
    parser.add_argument('tensor_name')
    parser.add_argument('values', nargs='*')
    parser.add_argument('--output_filepath', '-o', type=pathlib.Path)

    args = parser.parse_args()
    update_const(args.model_filepath, args.tensor_name, args.values, args.output_filepath)


if __name__ == '__main__':
    main()
