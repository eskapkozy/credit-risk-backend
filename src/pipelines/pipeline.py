import pandas as pd
from src.pipelines.Feature.fearurePipline import FeaturePipline


class Pipeline:
    def __init__(self, dataset: pd.DataFrame):
        self.dataset = dataset.copy()

        dataset = FeaturePipline(dataset)


