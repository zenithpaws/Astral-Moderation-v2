import argparse
import hashlib
import xml.etree.ElementTree as ET
import numpy as np


def print_weight_info(node_id, data_node, weights):
    shape = data_node.get('shape').strip()
    if shape:
        shape = [int(s) for s in shape.split(',')]
    else:
        shape = [1]

    offset = int(data_node.get('offset'))
    size = int(data_node.get('size'))

    sha1 = hashlib.sha1(weights[offset:offset+size]).hexdigest()

    print(f"{node_id}, {sha1}, {shape}")


def weights_hash(filename, bin_filename):
    tree = ET.parse(filename)
    root = tree.getroot()

    with open(bin_filename, 'rb') as f:
        weights = f.read()

    lines = []
    for layer in root.find('layers').findall('layer'):
        if layer.get('type') == 'Const':
            data_node = layer.find('data')
            print_weight_info(layer.get('id'), data_node, weights)


def main():
    parser = argparse.ArgumentParser('Get a summary of an OpenVino model')
    parser.add_argument('xml_filename', help='Filename for the input openvino XML file')
    parser.add_argument('bin_filename', help="Filename for the weights file")

    args = parser.parse_args()
    weights_hash(args.xml_filename, args.bin_filename)


if __name__ == '__main__':
    main()
