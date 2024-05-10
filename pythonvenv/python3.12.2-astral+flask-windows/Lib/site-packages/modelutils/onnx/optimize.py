import argparse
import pathlib
import onnx
import onnx.optimizer


def optimize(filepath, output_filepath, passes):
    model = onnx.load(filepath)

    # Add all initializer to inputs description in order to work around a crush issue in onnx.optimizer.
    existing_input_names = [i.name for i in model.graph.input]
    extra_inputs = []
    for initializer in model.graph.initializer:
        if initializer.name not in existing_input_names:
            info = onnx.helper.make_tensor_value_info(initializer.name, initializer.data_type, initializer.dims)
            model.graph.input.extend([info])
            extra_inputs.append(info.name)

    print("available passes: " + str(onnx.optimizer.get_available_passes()))
    print("applying: " + str(passes))
    model = onnx.optimizer.optimize(model, passes)

    # Remove the added inputs.
    current_inputs = list(model.graph.input)
    new_inputs = [i for i in current_inputs if i.name not in extra_inputs]
    del model.graph.input[:]
    model.graph.input.extend(new_inputs)

    onnx.checker.check_model(model)
    onnx.save(model, output_filepath)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('model_filepath', type=pathlib.Path)
    parser.add_argument('output_filepath', type=pathlib.Path)
    parser.add_argument('optimization_passes', nargs='*', default=['eliminate_unused_initializer', 'fuse_bn_into_conv'])

    args = parser.parse_args()
    if args.output_filepath.exists():
        parser.error(f"{args.output_filepath} already exists.")

    optimize(args.model_filepath, args.output_filepath, args.optimization_passes)


if __name__ == '__main__':
    main()
