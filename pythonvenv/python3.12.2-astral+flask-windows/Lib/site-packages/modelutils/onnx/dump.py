def dump_model(filepath):
    import onnx

    model = onnx.load(filepath)
    return str(model)
