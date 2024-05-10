import argparse
import os
import onnx
import onnx.numpy_helper
import numpy as np


def get_input_names(model):
    input_names = set(i.name for i in model.graph.input)
    init_names = set(i.name for i in model.graph.initializer)
    return list(input_names - init_names)


def convert(input_filename, output_filename, exclude_tensor_names):
    if os.path.exists(output_filename):
        raise RuntimeError(f"{output_filename} already exists.")

    model = onnx.load(input_filename)

    names = get_input_names(model)
    print(f"Detected input names: {names}")

    # Convert Cast operators
    for node in model.graph.node:
        if node.op_type == 'Cast':
            for attr in node.attribute:
                if attr.name == 'to' and attr.i == onnx.TensorProto.FLOAT:
                    attr.i = onnx.TensorProto.FLOAT16
                    break

    # Convert ConstantOfShape operators
    for node in model.graph.node:
        if node.op_type == 'ConstantOfShape':
            default_tensor = onnx.helper.make_tensor('value', onnx.TensorProto.FLOAT16, [1], [1])
            if not node.attribute:
                node.attribute.append(onnx.helper.make_attribute('value', default_tensor))
            else:
                for attr in node.attribute:
                    if attr.name == 'value' and attr.t.data_type == onnx.TensorProto.FLOAT:
                        array = onnx.numpy_helper.to_array(attr.t)
                        array = array.astype(np.float16)
                        del attr.t.dims[:]
                        del attr.t.float_data[:]
                        attr.t.MergeFrom(onnx.numpy_helper.from_array(array, attr.t.name))

    # Convert initializers to FP16
    for i, initializer in enumerate(model.graph.initializer):
        if initializer.data_type == onnx.TensorProto.DataType.FLOAT and initializer.name not in exclude_tensor_names:
            numpy_array = onnx.numpy_helper.to_array(initializer)
            numpy_array = numpy_array.astype(np.float16)
            del initializer.dims[:]
            del initializer.float_data[:]
            initializer.MergeFrom(onnx.numpy_helper.from_array(numpy_array, initializer.name))
            names.append(initializer.name)

    # Convert constant op to FP16
    for i, node in enumerate(model.graph.node):
        if node.op_type == 'Constant':
            for attr in node.attribute:
                if attr.name == 'value' and attr.t.data_type == onnx.TensorProto.DataType.FLOAT:
                    numpy_array = onnx.numpy_helper.to_array(attr.t)
                    numpy_array = numpy_array.astype(np.float16)
                    del attr.t.dims[:]
                    del attr.t.float_data[:]
                    attr.t.MergeFrom(onnx.numpy_helper.from_array(numpy_array, attr.t.name))

    # Modify input declaration to use FP16
    for input_decl in model.graph.input:
        if input_decl.name in names and input_decl.type.tensor_type.elem_type == onnx.TensorProto.DataType.FLOAT:
            input_decl.type.tensor_type.elem_type = onnx.TensorProto.DataType.FLOAT16

    # Modify output declaration to use FP16
    for output_decl in model.graph.output:
        if output_decl.type.tensor_type.elem_type == onnx.TensorProto.DataType.FLOAT:
            output_decl.type.tensor_type.elem_type = onnx.TensorProto.DataType.FLOAT16

    onnx.checker.check_model(model)
    onnx.save(model, output_filename)


def main():
    parser = argparse.ArgumentParser('Quantize ONNX model to FP16')
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)
    parser.add_argument('--exclude_tensor', type=str, nargs='+', default=[], help="The tensor names which should not be converted")

    args = parser.parse_args()

    convert(args.input_filepath, args.output_filepath, args.exclude_tensor)


if __name__ == '__main__':
    main()
