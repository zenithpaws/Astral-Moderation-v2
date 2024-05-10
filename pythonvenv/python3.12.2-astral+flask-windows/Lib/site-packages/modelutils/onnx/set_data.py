def set_data(model_filepath, name, value):
    import onnx
    import onnx.numpy_helper

    model = onnx.load(model_filepath)
    for initializer in model.graph.initializer:
        if initializer.name == name:
            new_tensor = onnx.numpy_helper.from_array(value, name=name)
            initializer.CopyFrom(new_tensor)
            return model.SerializeToString()

    return None
