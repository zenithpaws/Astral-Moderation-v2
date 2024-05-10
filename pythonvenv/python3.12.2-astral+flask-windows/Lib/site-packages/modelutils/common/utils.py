import io
import sys
import numpy as np


def read_input_npy(filepath):
    if not filepath and sys.stdin.isatty():
        raise RuntimeError("Please specify the npy_filepath or give npy file via stdin.")

    data = filepath.read_bytes() if filepath else sys.stdin.buffer.read()
    buf = io.BytesIO()
    buf.write(data)
    buf.seek(0)
    return np.load(buf, allow_pickle=True)


def write_output_npy(data):
    buf = io.BytesIO()
    np.save(buf, data)
    buf.seek(0)
    sys.stdout.buffer.write(buf.read())


def detect_type_from_suffix(filepath):
    KNOWN_SUFFIXES = {'.caffemodel': 'caffe',
                      '.mlmodel': 'coreml',
                      '.onnx': 'onnx',
                      '.pb': 'tensorflow',
                      '.prototxt': 'caffe',
                      '.pth': 'pytorch',
                      '.tflite': 'tensorflowlite',
                      '.xml': 'openvino'}

    for suffix in KNOWN_SUFFIXES:
        if suffix in filepath.suffixes:
            return KNOWN_SUFFIXES[suffix]

    return None
