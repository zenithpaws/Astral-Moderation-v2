def dump_model(filepath):
    import coremltools
    model = coremltools.models.MLModel(filepath).get_spec()
    return str(model)
