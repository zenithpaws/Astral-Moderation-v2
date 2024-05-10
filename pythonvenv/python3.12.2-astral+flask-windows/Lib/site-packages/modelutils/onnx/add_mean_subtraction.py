"""Add a mean subtraction layer to a ONNX model."""

import argparse
import pathlib
import numpy as np
import onnx
import onnx.numpy_helper


def _insert_node(model, node, index):
    node_list = list(model.graph.node)
    node_list.insert(index, node)
    del model.graph.node[:]
    model.graph.node.extend(node_list)


def _add_initializer(model, name, value):
    tensor = onnx.numpy_helper.from_array(value, name=name)
    model.graph.initializer.extend([tensor])


def add_mean_subtraction(input_filepath, output_filepath, mean_value):
    assert len(mean_value) == 3
    # There is an assumption that the input format is NCHW
    mean_value = np.array(mean_value, dtype=np.float32).reshape((3, 1, 1))
    model = onnx.load(input_filepath)

    assert len(model.graph.input) == 1
    input_name = model.graph.input[0].name

    input_nodes = [node for node in model.graph.node if input_name in node.input]
    assert len(input_nodes) == 1
    input_node = input_nodes[0]
    input_indexes = [i for i, name in enumerate(input_node.input) if name == input_name]
    assert len(input_indexes) == 1
    output_name = 'mean_subtracted'
    mean_value_name = 'mean_value'
    input_node.input[input_indexes[0]] = output_name

    _add_initializer(model, mean_value_name, mean_value)
    sub_node = onnx.helper.make_node('Sub', [input_name, mean_value_name], [output_name])
    _insert_node(model, sub_node, 0)

    onnx.checker.check_model(model)
    onnx.save(model, output_filepath)

    print(f"Saved a model to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Add a mean subtraction layer to a ONNX model")
    parser.add_argument('mean_value', nargs=3, type=float)
    parser.add_argument('input_filepath', type=pathlib.Path)
    parser.add_argument('output_filepath', type=pathlib.Path)

    args = parser.parse_args()

    if args.output_filepath.exists():
        parser.error(f"{args.output_filepath} already exists.")

    add_mean_subtraction(args.input_filepath, args.output_filepath, args.mean_value)


if __name__ == '__main__':
    main()
