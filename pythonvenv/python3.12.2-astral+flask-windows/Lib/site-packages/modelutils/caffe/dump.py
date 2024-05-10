def dump_model(filepath):
    from caffe.proto import caffe_pb2

    model = caffe_pb2.NetParameter()
    model.ParseFromString(filepath.read_bytes())
    return str(model)
