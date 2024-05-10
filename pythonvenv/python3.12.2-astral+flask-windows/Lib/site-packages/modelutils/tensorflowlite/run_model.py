def run_model(model_filepath, input_array, output_names):
    import tensorflow
    interpreter = tensorflow.lite.Interpreter(model_path=str(model_filepath))
    interpreter.allocate_tensors()

    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    interpreter.set_tensor(input_details[0]['index'], input_array)
    interpreter.invoke()

    if output_names:
        name_mappings = {d['name']: d['index'] for d in interpreter.get_tensor_details()}
        output_indexes = {n: name_mappings[n] for n in output_names}
    else:
        output_indexes = {d['name']: d['index'] for d in output_details}

    return {name: interpreter.get_tensor(index) for name, index in output_indexes.items()}
