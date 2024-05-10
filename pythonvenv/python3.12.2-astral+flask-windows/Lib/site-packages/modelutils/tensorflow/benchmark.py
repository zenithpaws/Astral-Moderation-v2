import argparse
import time
import numpy as np
import tensorflow as tf
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


def benchmark(model_filepath, image_filepath):
    graph_def = tf.compat.v1.GraphDef()
    with open(model_filepath, 'rb') as f:
        graph_def.ParseFromString(f.read())
    tf.import_graph_def(graph_def, name='')

    graph_in, graph_out = get_graph_inputs_outputs(graph_def)

    assert len(graph_in) == 1
    input_tensor_name = graph_in[0] + ':0'
    output_names = [o + ':0' for o in graph_out]

    with tf.compat.v1.Session() as sess:
        input_tensor_shape = sess.graph.get_tensor_by_name(input_tensor_name).shape.as_list()
        output_tensors = [sess.graph.get_tensor_by_name(o) for o in output_names]

    if image_filepath:
        inputs = preprocess_inputs(image_filepath, input_tensor_shape[1:3])
    else:
        inputs = np.random.rand(1, *input_tensor_shape[1:3], 3)
    inputs = inputs.astype(np.float32)

    with monitor("First run"):
        with tf.compat.v1.Session() as sess:
            sess.run(output_tensors, {input_tensor_name: inputs})

    with monitor("100 run"):
        with tf.compat.v1.Session() as sess:
            for i in range(100):
                sess.run(output_tensors, {input_tensor_name: inputs})


def get_graph_inputs_outputs(graph_def):
    input_names = []
    inputs_set = set()
    outputs_set = set()

    for node in graph_def.node:
        if node.op == 'Placeholder':
            input_names.append(node.name)

        for i in node.input:
            inputs_set.add(i.split(':')[0])
        outputs_set.add(node.name)

    output_names = list(outputs_set - inputs_set)
    return input_names, output_names


def preprocess_inputs(image_filename, input_shape, is_bgr=True, normalize_inputs=False, subtract_inputs=[]):
    image = Image.open(image_filename)
    image = image.resize(input_shape, Image.ANTIALIAS)
    image = image.convert('RGB') if image.mode != 'RGB' else image
    image = np.asarray(image, dtype=np.float32)

    if subtract_inputs:
        assert len(subtract_inputs) == 3
        image -= np.array(subtract_inputs, dtype=np.float32)

    image = image[:, :, (2, 1, 0)] if is_bgr else image  # RGB -> BGR
    image = image[np.newaxis, :]

    if normalize_inputs:
        image /= 255
    return image


def main():
    parser = argparse.ArgumentParser("Benchmark a TensorFlow model")
    parser.add_argument('model_filename', type=str, help="Tensorflow model to use")
    parser.add_argument('--image_filename', type=str, default=None, help="Image file to use. If not provided, use a random tensor as input")

    args = parser.parse_args()

    benchmark(args.model_filename, args.image_filename)


if __name__ == '__main__':
    main()
