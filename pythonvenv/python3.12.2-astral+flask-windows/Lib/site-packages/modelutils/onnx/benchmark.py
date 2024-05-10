import argparse
import time
import numpy as np
import onnxruntime
from PIL import Image
from contextlib import contextmanager

DEVICE_ID = 0


@contextmanager
def monitor(prefix=""):
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print(f"{prefix:<20}: {end-start}s")


def benchmark(onnx_model_filepath, image_filepath):
    sess = onnxruntime.InferenceSession(onnx_model_filepath)
    output_names = [o.name for o in sess.get_outputs()]
    input_name = sess.get_inputs()[0].name

    input_shape = sess.get_inputs()[0].shape
    print(f"Input shape: {input_shape}")
    if image_filepath:
        inputs = preprocess_inputs(image_filepath, input_shape[2:])
    else:
        inputs = np.random.rand(1, *input_shape[1:])
    inputs = inputs.astype(get_data_type(sess.get_inputs()[0].type))

    with monitor("First run"):
        sess.run(output_names, {input_name: inputs})

    with monitor("100 run"):
        for i in range(100):
            sess.run(output_names, {input_name: inputs})


def get_data_type(type_name):
    if type_name == 'tensor(float16)':
        return np.float16
    else:  # TODO
        return np.float32


def preprocess_inputs(image_filename, input_shape, is_bgr=True, normalize_inputs=False, subtract_inputs=[]):
    image = Image.open(image_filename)
    image = image.resize(input_shape, Image.ANTIALIAS)
    image = image.convert('RGB') if image.mode != 'RGB' else image
    image = np.asarray(image, dtype=np.float32)

    if subtract_inputs:
        assert len(subtract_inputs) == 3
        image -= np.array(subtract_inputs, dtype=np.float32)

    image = image[:, :, (2, 1, 0)] if is_bgr else image  # RGB -> BGR
    image = image.transpose((2, 0, 1))
    image = image[np.newaxis, :]

    if normalize_inputs:
        image /= 255
    return image


def main():
    parser = argparse.ArgumentParser("Benchmark an ONNX model")
    parser.add_argument('onnx_model', help="Onnx model to use")
    parser.add_argument('--image_filename', default=None, help="Image file to use. If not provided, use a random tensor as input")

    args = parser.parse_args()

    benchmark(args.onnx_model, args.image_filename)


if __name__ == '__main__':
    main()
