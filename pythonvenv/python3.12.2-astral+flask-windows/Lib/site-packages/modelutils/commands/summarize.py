import argparse
import pathlib
from ..common.summarizer import ModelNodesSummarizer, ModelWeightsSummarizer
from ..caffe.summarize import parse_model as caffe_parse_model
from ..onnx.summarize import parse_model as onnx_parse_model
from ..openvino.summarize import parse_model as openvino_parse_model


KNOWN_SUFFIX = {'.prototxt': 'caffe',
                '.xml': 'openvino',
                '.onnx': 'onnx'}

HANDLERS = {'caffe': caffe_parse_model,
            'openvino': openvino_parse_model,
            'onnx': onnx_parse_model}


def summarize(model_filepaths, model_type):
    if not model_type and model_filepaths[0].suffix in KNOWN_SUFFIX:
        model_type = KNOWN_SUFFIX[model_filepaths[0].suffix]

    if not model_type:
        raise RuntimeError("Failed to detect the model type")

    handler = HANDLERS[model_type]

    model = handler(*model_filepaths)

    model.validate()
    summarizers = [ModelNodesSummarizer, ModelWeightsSummarizer]
    for s in summarizers:
        summarizer = s()
        summarizer.summarize(model)


def main():
    parser = argparse.ArgumentParser("Get a summary of a model")
    parser.add_argument('model_filepaths', nargs='+', type=pathlib.Path, help="File path to the model. If the model has multiple files, specify a file which represents graph structure first.")
    parser.add_argument('--model_type', '-t', choices=HANDLERS.keys())

    args = parser.parse_args()
    summarize(args.model_filepaths, args.model_type)
