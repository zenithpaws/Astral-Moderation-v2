import argparse
import json
import numpy as np
import tensorflow as tf


def get_weights_from_graph_def(graph_def, tensor_name):
    for node in graph_def.node:
        if node.op == 'Const' and node.name == tensor_name:
            return tf.make_ndarray(node.attr['value'].tensor)

    return None


def update_weights_manifest_shape(manifest, tensor_name, shape):
    for entry in manifest['weightsManifest'][0]['weights']:
        if entry['name'] == tensor_name:
            entry['shape'] = list(shape)
            return True

    return False


def copy_weights_to_tensorflowjs(pb_filename, tfjs_json_filename, tfjs_bin_filename, tensor_names):
    graph_def = tf.compat.v1.GraphDef()
    with open(pb_filename, 'rb') as f:
        graph_def.ParseFromString(f.read())

    with open(tfjs_json_filename, 'r') as f:
        manifest = json.load(f)

    with open(tfjs_bin_filename, 'rb') as f:
        weights_bin = f.read()

    # Read weights from tfjs_bin_file.
    weights = {}
    offset = 0
    for entry in manifest['weightsManifest'][0]['weights']:
        weight_numel = 1
        for dim in entry['shape']:
            weight_numel *= dim

        weights[entry['name']] = np.frombuffer(weights_bin, dtype=entry['dtype'], count=weight_numel, offset=offset)
        offset += np.dtype(entry['dtype']).itemsize * weight_numel

    # Read weights from PB model and overwrite an internal weights dictionary.
    for tensor_name in tensor_names:
        weights[tensor_name] = get_weights_from_graph_def(graph_def, tensor_name)
        if not update_weights_manifest_shape(manifest, tensor_name, weights[tensor_name].shape):
            raise RuntimeError

    # Write manifest
    with open(tfjs_json_filename + '.new', 'w') as f:
        json.dump(manifest, f)

    # Write bin file
    with open(tfjs_bin_filename + '.new', 'wb') as f:
        for entry in manifest['weightsManifest'][0]['weights']:
            w = weights[entry['name']]
            f.write(w.tobytes())


def main():
    parser = argparse.ArgumentParser("Copy weights from TensorFlow model to TensorFLow.js model")
    parser.add_argument('pb_filename', type=str, help="Filename for the TensorFlow model")
    parser.add_argument('tfjs_json_filename', type=str, help="Filename for the TensorFlow.js json file")
    parser.add_argument('tfjs_bin_filename', type=str, help="Filename for the TensorFlow.js bin file")
    parser.add_argument('--tensor_name', type=str, nargs='+', help="Tensor name to be copied")

    args = parser.parse_args()
    copy_weights_to_tensorflowjs(args.pb_filename, args.tfjs_json_filename, args.tfjs_bin_filename, args.tensor_name)


if __name__ == '__main__':
    main()
