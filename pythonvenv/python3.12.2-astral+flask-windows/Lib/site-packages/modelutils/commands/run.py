import argparse
import pathlib
from ..common.utils import read_input_npy, write_output_npy, detect_type_from_suffix
from ..caffe.run_model import run_model as caffe_run_model
from ..onnx.run_model import run_model as onnx_run_model
from ..openvino.run_model import run_model as openvino_run_model
from ..tensorflow.run_model import run_model as tf_run_model
from ..tensorflowlite.run_model import run_model as tflite_run_model

HANDLERS = {'caffe': caffe_run_model,
            'onnx': onnx_run_model,
            'openvino': openvino_run_model,
            'tensorflow': tf_run_model,
            'tensorflowlite': tflite_run_model}


def run(model_filepath, input_filepath, output_names):
    assert isinstance(model_filepath, list)

    input_data = read_input_npy(input_filepath)
    assert len(input_data.shape) == 4
    model_type = detect_type_from_suffix(model_filepath[0])
    if not model_type or model_type not in HANDLERS:
        raise RuntimeError(f"Unknown extension: {model_filepath}")

    handler = HANDLERS[model_type]
    model_filepath = model_filepath[0] if len(model_filepath) == 1 else model_filepath
    outputs = handler(model_filepath, input_data, output_names)

    write_output_npy(outputs)


def main():
    parser = argparse.ArgumentParser("Run a model")
    parser.add_argument('model_filepath', nargs='+', type=pathlib.Path)
    parser.add_argument('input_filepath', type=pathlib.Path, nargs='?', help="Input npy filepath. If not given, read numpy array from stdin.")
    parser.add_argument('--output_name', nargs='*')

    args = parser.parse_args()
    run(args.model_filepath, args.input_filepath, args.output_name)


if __name__ == '__main__':
    main()
