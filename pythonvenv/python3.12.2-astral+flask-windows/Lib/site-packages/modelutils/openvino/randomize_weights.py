import argparse
import pathlib
import xml.etree.ElementTree as ET
import numpy as np


def _randomize(weights_bytes, data_node):
    shape = data_node.get('shape').strip()
    if shape:
        shape = [int(s) for s in shape.split(',')]
    else:
        shape = [1]
    dtype = {'f32': np.float32, 'f16': np.float16}[data_node.get('element_type')]
    offset = int(data_node.get('offset'))
    size = int(data_node.get('size'))
    randomized_weights = np.random.rand(*shape).astype(dtype).tobytes()
    assert len(randomized_weights) == size
    weights_bytes[offset:offset+size] = randomized_weights


def randomize_weights(xml_filepath, bin_filepath, output_bin_filepath):
    root = ET.parse(xml_filepath).getroot()

    weights_bytes = bytearray(bin_filepath.read_bytes())

    for layer in root.find('layers').findall('layer'):
        if layer.get('type') == 'Const':
            data_node = layer.find('data')
            if data_node.get('element_type') in ['f32', 'f16']:
                _randomize(weights_bytes, data_node)

    output_bin_filepath.write_bytes(weights_bytes)
    print(f"Saved to {output_bin_filepath}")


def main():
    parser = argparse.ArgumentParser(description="Randomize the weights of OpenVino model")
    parser.add_argument('xml_filepath', type=pathlib.Path)
    parser.add_argument('bin_filepath', type=pathlib.Path)
    parser.add_argument('--output_bin_filepath', type=pathlib.Path)

    args = parser.parse_args()
    if not args.xml_filepath.exists() or not args.bin_filepath.exists():
        parser.error(f"Input files are missing: {args.xml_filepath}, {args.bin_filepath}")

    if not args.output_bin_filepath:
        args.output_bin_filepath = pathlib.Path(str(args.bin_filepath) + '.random')

    if args.output_bin_filepath.exists():
        parser.error(f"{args.output_bin_filepath} already exists.")

    randomize_weights(args.xml_filepath, args.bin_filepath, args.output_bin_filepath)


if __name__ == '__main__':
    main()
