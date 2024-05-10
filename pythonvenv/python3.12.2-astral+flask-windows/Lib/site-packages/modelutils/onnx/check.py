import argparse
import pathlib
import onnx


def check(model_filepath):
    model = onnx.load(model_filepath)
    onnx.checker.check_model(model)


def main():
    parser = argparse.ArgumentParser(description="Check the model")
    parser.add_argument('model_filepath', type=pathlib.Path)

    args = parser.parse_args()
    check(args.model_filepath)


if __name__ == '__main__':
    main()
