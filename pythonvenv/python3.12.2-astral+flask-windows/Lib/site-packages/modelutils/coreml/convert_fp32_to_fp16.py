import argparse
import coremltools


def convert(input_filename, output_filename):
    model_spec = coremltools.utils.load_spec(input_filename)
    model_fp16 = coremltools.utils.convert_neural_network_spec_weights_to_fp16(model_spec)
    coremltools.utils.save_spec(model_fp16, output_filename)


def main():
    parser = argparse.ArgumentParser('Quantize CoreML model to FP16')
    parser.add_argument('input_filepath', type=str)
    parser.add_argument('output_filepath', type=str)

    args = parser.parse_args()

    convert(args.input_filepath, args.output_filepath)


if __name__ == '__main__':
    main()
