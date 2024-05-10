import argparse
import hashlib
import onnx
import onnx.numpy_helper


def weights_hash(filename):
    model = onnx.load(filename)

    for initializer in model.graph.initializer:
        data = onnx.numpy_helper.to_array(initializer)
        sha1 = hashlib.sha1(data.tobytes()).hexdigest()
        print(f"{initializer.name}, {sha1}, {data.shape}")


def main():
    parser = argparse.ArgumentParser("Get hashes of ONNX model weights")
    parser.add_argument('model_filename', help="Filename for the input onnx file")

    args = parser.parse_args()
    weights_hash(args.model_filename)


if __name__ == '__main__':
    main()
