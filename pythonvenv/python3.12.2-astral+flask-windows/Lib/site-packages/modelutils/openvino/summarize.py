import collections
import xml.etree.ElementTree as ET
import numpy as np
from ..common.model import Model


class ConvolutionTransformer:
    def transform(self, model):
        output_maps = collections.defaultdict(list)
        for n in model.nodes.values():
            for i in n.inputs:
                output_maps[i].append(n)

        node_names_to_be_removed = set()
        for node in model.nodes.values():
            if node.op in ['Convolution', 'GroupConvolution'] and len(node.inputs) == 2:
                outputs = output_maps[node.name]
                if len(outputs) == 1 and outputs[0].op == 'Add' and outputs[0].inputs[1] in model.data:
                    add_node = outputs[0]
                    node.inputs.append(add_node.inputs[1])
                    add_outputs = output_maps[add_node.name]
                    for o in add_outputs:
                        o.inputs = [i if i != add_node.name else node.name for i in o.inputs]
                    node_names_to_be_removed.add(add_node.name)

        for name in node_names_to_be_removed:
            model.remove_node(name)


class OpenVinoModelParser:
    def __init__(self, xml_filepath, bin_filepath):
        tree = ET.parse(xml_filepath)
        self.root = tree.getroot()
        self.weights = bin_filepath and bin_filepath.read_bytes()

    def parse(self):
        inputs = self._parse_edges()
        model = Model()
        for layer in self.root.find('layers').findall('layer'):
            layer_id = layer.get('id')
            op = layer.get('type')
            name = layer.get('name')
            attrs = {'name': name}
            if op == 'Const':
                model.add_data(layer_id, self._read_weights(layer.find('data')))
            elif op != 'Parameter':  # Ignore parameter node. Our abstract Model doesn't require Input node.
                model.add_node(op, layer_id, inputs[layer_id], attrs)
        return model

    def _read_weights(self, data_attrs):
        offset = int(data_attrs.get('offset'))
        shape_str = data_attrs.get('shape')
        shape = [int(i) for i in shape_str.split(',')] if shape_str else [1]
        element_type = data_attrs.get('element_type')

        count = np.product(shape)
        dtype = {'f32': np.float32, 'i32': np.int32, 'i64': np.int64}[element_type]
        if self.weights:
            buf = np.frombuffer(self.weights, dtype, count, offset)
        else:
            buf = np.zeros(shape, dtype)
        return buf.reshape(shape)

    def _parse_edges(self):
        inputs = collections.defaultdict(dict)
        for edge in self.root.find('edges').findall('edge'):
            from_layer = edge.get('from-layer')
            # Ignore from_port for now.
            # from_port = edge.get('from-port')
            to_layer = edge.get('to-layer')
            to_port = int(edge.get('to-port'))
            inputs[to_layer][to_port] = from_layer

        results = collections.defaultdict(list)
        for to_layer, ports in inputs.items():
            results[to_layer] = [ports[i] for i in range(len(ports))]
        return results


def parse_model(xml_filepath, bin_filepath):
    parser = OpenVinoModelParser(xml_filepath, bin_filepath)
    model = parser.parse()
    ConvolutionTransformer().transform(model)
    return model
