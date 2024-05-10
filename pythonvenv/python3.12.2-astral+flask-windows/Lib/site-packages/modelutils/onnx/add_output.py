import argparse
import pathlib
import onnx


def add_output(onnx_filepath, output_filepath, output_name):
    model = onnx.ModelProto()
    model.ParseFromString(onnx_filepath.read_bytes())

    existing_output_names = [o.name for o in model.graph.output]
    print(f"Existing output names: {existing_output_names}")

    new_names = [n for n in output_name if n not in existing_output_names]
    for name in new_names:
        model.graph.output.append(onnx.helper.make_tensor_value_info(name, onnx.TensorProto.FLOAT, None))
        print(f"Added output: {name}")

    if output_name and output_filepath:
        output_filepath.write_bytes(model.SerializeToString())
        print(f"Saved to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Add output nodes to ONNX model")
    parser.add_argument('onnx_filepath', type=pathlib.Path)
    parser.add_argument('output_filepath', nargs='?', type=pathlib.Path)
    parser.add_argument('--output_name', nargs='+', default=[])

    args = parser.parse_args()

    if args.output_filepath and args.output_filepath.exists():
        parser.error(f"{args.output_filepath} already exists.")

    add_output(args.onnx_filepath, args.output_filepath, args.output_name)


if __name__ == '__main__':
    main()
