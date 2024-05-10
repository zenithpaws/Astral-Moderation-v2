import argparse
import pathlib
import xml.etree.ElementTree as ET
import numpy as np


def update_const(xml_input_filepath, bin_input_filepath, bin_output_filepath, node_id, new_value):
    tree = ET.parse(xml_input_filepath)
    for layer in tree.getroot().find('layers').findall('layer'):
        if layer.get('id') == node_id:
            data_node = layer.find('data')
            offset = int(data_node.get('offset'))
            size = int(data_node.get('size'))
            element_type = data_node.get('element_type')
            shape_str = data_node.get('shape')
            if not shape_str:
                shape_str = "1"
            shape = [int(s) for s in shape_str.split(',')]
            count = np.prod(shape)

    with open(bin_input_filepath, 'rb') as f:
        weights = f.read()

    dtype = {'f32': np.float32, 'i32': np.int32, 'i64': np.int64}[element_type]

    old_np_array = np.frombuffer(weights, dtype, count, offset)
    print(f"Old values are: {old_np_array}")

    if new_value:
        new_value = [float(i) for i in new_value] # TODO
        new_np_array = np.array(new_value, dtype=dtype)
        assert new_np_array.nbytes == size
        print(f"New values are: {new_np_array}")

        with open(bin_output_filepath, 'wb') as f:
            f.write(weights[:offset])
            f.write(new_np_array.tobytes())
            f.write(weights[offset+size:])


def main():
    parser = argparse.ArgumentParser(description="Add a new const node to OpenVino model")
    parser.add_argument('xml_input_filepath', type=pathlib.Path)
    parser.add_argument('bin_input_filepath', type=pathlib.Path)
    parser.add_argument('node_id')
    parser.add_argument('values', nargs='*')
    parser.add_argument('--bin_output_filepath', '-o', type=pathlib.Path)

    args = parser.parse_args()
    update_const(args.xml_input_filepath, args.bin_input_filepath, args.bin_output_filepath, args.node_id, args.values)


if __name__ == '__main__':
    main()
