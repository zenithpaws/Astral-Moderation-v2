from google.protobuf import text_format


def load_model(in_filename, out_filename):
    import onnx
    model = onnx.ModelProto()
    with open(in_filename, 'r') as f:
        text_format.Parse(f.read(), model)

    onnx.save(model, out_filename)
