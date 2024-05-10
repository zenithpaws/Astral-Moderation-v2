import argparse
import pathlib
from ..common.utils import write_output_npy, detect_type_from_suffix
from ..caffe.get_data import get_data as caffe_get_data
from ..onnx.get_data import get_data as onnx_get_data
from ..pytorch.get_data import get_data as pytorch_get_data
from ..tensorflow.get_data import get_data as tf_get_data
from ..tensorflowlite.get_data import get_data as tflite_get_data

HANDLERS = {'caffe': caffe_get_data,
            'onnx': onnx_get_data,
            'pytorch': pytorch_get_data,
            'tensorflow': tf_get_data,
            'tensorflowlite': tflite_get_data}


def getdata(model_filepath, name, model_type):
    model_type = model_type or detect_type_from_suffix(model_filepath)
    if not model_type:
        raise RuntimeError("Failed to detect the model type. Please specify explicitly.")

    if model_type not in HANDLERS:
        raise NotImplementedError()

    handler = HANDLERS[model_type]
    data = handler(model_filepath, name)
    write_output_npy(data)


def main():
    parser = argparse.ArgumentParser(description="Get const data from a model")
    parser.add_argument('model_filepath', type=pathlib.Path)
    parser.add_argument('--name', '-n', help="Name of the data to get. If not specified, returns all of them.")
    parser.add_argument('--type', '-t', choices=HANDLERS.keys())

    args = parser.parse_args()
    getdata(args.model_filepath, args.name, args.type)
