import numpy as np


class Summarizer:
    pass


class ModelNodesSummarizer(Summarizer):
    def summarize(self, model):
        print("===== model summary =====")
        print(model)


class ModelWeightsSummarizer(Summarizer):
    def summarize(self, model):
        print("===== weights summary =====")
        for name, data in model.data.items():
            min_value = np.amin(data)
            max_value = np.amax(data)
            mean_value = np.mean(data)
            print(f"{name}, {data.shape}, {data.dtype} mean: {mean_value}, min: {min_value}, max: {max_value}")
