import argparse
import pathlib
from ..caffe.load import load_model as caffe_load_model
from ..common.utils import detect_type_from_suffix
from ..onnx.load import load_model as onnx_load_model
from ..tensorflow.load import load_model as tensorflow_load_model


HANDLERS = {'caffe': caffe_load_model,
            'onnx': onnx_load_model,
            'tensorflow': tensorflow_load_model}


def load(input_filepath, output_filepath, model_type):
    model_type = model_type or detect_type_from_suffix(input_filepath)
    if not model_type:
        raise RuntimeError("Failed to detect model type from suffixes. Please specify the model type explicitly.")

    if model_type not in HANDLERS:
        raise NotImplementedError(f"{model_type} is not supported yet.")

    handler = HANDLERS[model_type]
    handler(input_filepath, output_filepath)
    print(f"Saved to {output_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Load a model from text format")
    parser.add_argument('text_filepath', type=pathlib.Path, help="File path to the model file.")
    parser.add_argument('output_filepath', type=pathlib.Path, help="Output filepath.")
    parser.add_argument('--type', '-t', choices=HANDLERS.keys())

    args = parser.parse_args()
    if not args.text_filepath.exists():
        parser.error(f"{args.text_filepath} is not found.")

    if args.output_filepath.exists():
        parser.error(f"{args.output_filepath} already exists.")

    load(args.text_filepath, args.output_filepath, args.type)


if __name__ == '__main__':
    main()
