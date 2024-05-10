import tempfile
import xml.etree.ElementTree as ET


def _get_output_port(tree, name):
    """Get the first output id of the specified layer."""
    for layer in tree.getroot().find('layers').findall('layer'):
        if layer.get('name') == name:
            for port in layer.find('output').findall('port'):
                return int(port.get('id'))


def _add_outputs(ie, xml_filepath, bin_filepath, additional_outputs):
    """Add new outputs to the model and load it."""
    tree = ET.parse(xml_filepath)
    layers = tree.getroot().find('layers')
    edges = tree.getroot().find('edges')
    layer_ids = {layer.get('name'): int(layer.get('id')) for layer in layers.findall('layer')}
    max_layer_id = max(layer_ids.values())

    for new_output in additional_outputs:
        layer = ET.SubElement(layers, 'layer', id=str(max_layer_id+1), name=f'{new_output}/result', type='Result', version='opset1')
        input_node = ET.SubElement(layer, 'input')
        ET.SubElement(input_node, 'port', id='0')
        ET.SubElement(edges, 'edge', **{'from-layer': str(layer_ids[new_output]), 'from-port': str(_get_output_port(tree, new_output)), 'to-layer': str(max_layer_id+1), 'to-port': '0'})
        max_layer_id += 1

    with tempfile.NamedTemporaryFile() as temp_file:
        tree.write(temp_file.name)
        return ie.read_network(temp_file.name, str(bin_filepath))


def run_model(model_filepath, input_array, output_names):
    assert len(model_filepath) == 2, "OpenVino requires two model files: .xml and .bin"
    from openvino.inference_engine import IECore
    ie = IECore()
    net = ie.read_network(str(model_filepath[0]), str(model_filepath[1]))
    assert len(net.inputs) == 1
    input_name = list(net.inputs.keys())[0]
    output_names = output_names or list(net.outputs.keys())

    additional_outputs = set(output_names) - set(net.outputs.keys())
    if additional_outputs:
        net = _add_outputs(ie, model_filepath[0], model_filepath[1], additional_outputs)

    # TODO: Extract intermediate layers.
    exec_net = ie.load_network(network=net, device_name='CPU')
    outputs = exec_net.infer(inputs={input_name: input_array})

    return {name: outputs[name] for name in output_names}
