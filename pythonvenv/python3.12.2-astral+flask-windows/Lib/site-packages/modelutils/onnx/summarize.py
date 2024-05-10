import onnx
import onnx.numpy_helper
from ..common.model import Model


class OnnxModelParser:
    def __init__(self, model_filepath):
        self.model = onnx.load(model_filepath)

    def parse(self):
        model = Model()
        for node in self.model.graph.node:
            # TODO: ONNX can have multiple outputs, but our abstract Model cannot. Need to fix it.
            for output_name in node.output:
                model.add_node(node.op_type, output_name, node.input, {'name': node.name})

        for initializer in self.model.graph.initializer:
            data = onnx.numpy_helper.to_array(initializer)
            model.add_data(initializer.name, data)

        return model


def parse_model(filepath):
    parser = OnnxModelParser(filepath)
    model = parser.parse()

    onnx_model = onnx.load(filepath)

    # Get the opset version for the default opset.
    opset_version = -1
    for opset in onnx_model.opset_import:
        if opset.domain == "":
            opset_version = opset.version

    model.add_attr('ir_version', onnx_model.ir_version)
    model.add_attr('opset_version', opset_version)

    return model
