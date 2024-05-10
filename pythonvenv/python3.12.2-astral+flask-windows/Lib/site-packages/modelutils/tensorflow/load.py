from google.protobuf import text_format


def load_graphdef(in_filename, out_filename):
    import tensorflow
    model = tensorflow.compat.v1.GraphDef()
    with open(in_filename, 'r') as f:
        text_format.Parse(f.read(), model)

    with open(out_filename, 'wb') as f:
        f.write(model.SerializeToString())


def load_savedmodel(in_filename, out_filename):
    from tensorflow.core.protobuf import saved_model_pb2
    saved_model_def = saved_model_pb2.SavedModel()

    with open(in_filename, 'r') as f:
        text_format.Parse(f.read(), saved_model_def)

    with open(out_filename, 'wb') as f:
        f.write(saved_model_def.SerializeToString())


def load_model(in_filename, out_filename):
    try:
        load_graphdef(in_filename, out_filename)
    except Exception:
        load_savedmodel(in_filename, out_filename)
