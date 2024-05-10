import argparse
import xml.etree.ElementTree as ET
import numpy as np


def add_const(xml_input_filepath, bin_input_filepath, value_type, values):
    assert value_type in ['f32', 'i32', 'i64']
    dtype = {'f32': np.float32, 'i32': np.int32, 'i64': np.int64}[value_type]
    np_value = np.array(values, dtype=dtype)

    output_xml_filepath = xml_input_filepath + '.new'
    output_bin_filepath = bin_input_filepath + '.new'

    with open(bin_input_filepath, 'rb') as f:
        weights = f.read()

    offset = len(weights)
    size = np_value.nbytes

    with open(output_bin_filepath, 'wb') as f:
        f.write(weights)
        f.write(np_value.tobytes())

    tree = ET.parse(xml_input_filepath)
    all_ids = [layer.get('id') for layer in tree.getroot().find('layers').findall('layer')]
    node_id = max([int(i) for i in all_ids]) + 1
    shape = str(len(values))
    precision = {'f32': 'FP32', 'i32': 'I32', 'i64': 'I64'}[value_type]

    layer = ET.SubElement(tree.getroot().find('layers'), 'layer', id=str(node_id), name=f'const_{node_id}', type='Const', version='opset1')
    ET.SubElement(layer, 'data', element_type=value_type, offset=str(offset), shape=shape, size=str(size))
    output = ET.SubElement(layer, 'output')
    port = ET.SubElement(output, 'port', id='1', precision=precision)
    dim = ET.SubElement(port, 'dim')
    dim.text = str(len(values))

    tree.write(output_xml_filepath)
    print(f"Added node {node_id}")


def main():
    parser = argparse.ArgumentParser("Add a new const node to OpenVino model")
    parser.add_argument('xml_input_filepath')
    parser.add_argument('bin_input_filepath')
    parser.add_argument('value_type', choices=['f32', 'i32', 'i64'])
    parser.add_argument('values', nargs='*')

    args = parser.parse_args()
    add_const(args.xml_input_filepath, args.bin_input_filepath, args.value_type, args.values)


if __name__ == '__main__':
    main()
