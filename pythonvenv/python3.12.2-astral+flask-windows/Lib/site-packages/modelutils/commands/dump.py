import argparse
import pathlib
from ..caffe.dump import dump_model as caffe_dump_model
from ..common.utils import detect_type_from_suffix
from ..coreml.dump import dump_model as coreml_dump_model
from ..onnx.dump import dump_model as onnx_dump_model
from ..tensorflow.dump import dump_model as tensorflow_dump_model


HANDLERS = {'caffe': caffe_dump_model,
            'coreml': coreml_dump_model,
            'onnx': onnx_dump_model,
            'tensorflow': tensorflow_dump_model}


def dump(model_filepath, output_filepath, model_type):
    model_type = model_type or detect_type_from_suffix(model_filepath)
    if not model_type:
        raise RuntimeError("Failed to detect model type from suffixes. Please specify the model type explicitly.")

    if model_type not in HANDLERS:
        raise NotImplementedError(f"{model_type} is not supported yet.")

    handler = HANDLERS[model_type]
    dumped_model = handler(model_filepath)

    if output_filepath:
        output_filepath.write_text(dumped_model)
    else:
        print(dumped_model)


def main():
    parser = argparse.ArgumentParser(description="Dump a model into text format")
    parser.add_argument('model_filepath', type=pathlib.Path, help="File path to the model file.")
    parser.add_argument('--output', '-o', nargs='?', type=pathlib.Path, default=False, metavar='FILEPATH', help="Save to a file.")
    parser.add_argument('--type', '-t', choices=HANDLERS.keys())

    args = parser.parse_args()
    if not args.model_filepath.exists():
        parser.error(f"{args.model_filepath} is not found.")

    if args.output is None:
        args.output = pathlib.Path(str(args.model_filepath) + '.dump')

    if args.output and args.output.exists():
        parser.error(f"{args.output} already exists.")

    dump(args.model_filepath, args.output, args.type)


if __name__ == '__main__':
    main()
