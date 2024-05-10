from google.protobuf import text_format


def load_model(input_filepath, output_filepath):
    from caffe.proto import caffe_pb2
    net = caffe_pb2.NetParameter()
    text_format.Parse(input_filepath.read_text(), net)
    output_filepath.write_bytes(net.SerializeToString())
