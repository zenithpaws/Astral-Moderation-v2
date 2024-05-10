def dump_model(filepath):
    import tensorflow
    try:
        graph_def = tensorflow.compat.v1.GraphDef()
        graph_def.ParseFromString(filepath.read_bytes())
        return str(graph_def)
    except Exception:
        # Try SavedModel format.
        from tensorflow.core.protobuf import saved_model_pb2
        saved_model_def = saved_model_pb2.SavedModel()
        saved_model_def.ParseFromString(filepath.read_bytes())
        return str(saved_model_def)
