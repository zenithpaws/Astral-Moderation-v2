def get_data(model_filepath, name):
    import caffe.io
    from caffe.proto import caffe_pb2
    weights = caffe_pb2.NetParameter()
    weights.ParseFromString(model_filepath.read_bytes())

    if name:
        for layer in weights.layer:
            if layer.name == name:
                return {f'{name}_{i}': caffe.io.blobproto_to_array(blob) for i, blob in enumerate(layer.blobs)}

    all_results = {}
    for layer in weights.layer:
        for i, blob in enumerate(layer.blobs):
            all_results[f'{layer.name}_{i}'] = caffe.io.blobproto_to_array(blob)
    return all_results
