import os


def run_model(model_filepath, input_array, output_names):
    os.environ['GLOG_minloglevel'] = '2'  # Suppress caffe warnings.
    import caffe
    assert len(model_filepath) == 2, "Caffe requires two model files: .prototxt and .caffemodel"
    net = caffe.Net(str(model_filepath[0]), caffe.TEST, weights=str(model_filepath[1]))

    assert len(net.inputs) == 1
    input_blob = net.blobs[net.inputs[0]]
    input_blob.reshape(*input_array.shape)
    input_blob.data[...] = input_array

    net.forward()

    output_names = output_names or net.outputs
    return {name: net.blobs[name].data for name in output_names}
