import pandas as pd

class Behavior:

    def __init__(self, dataset: pd.DataFrame, mapping: dict):
        self.dataset = dataset.copy()
        self.mapping = mapping

        self.historical = mapping['historique du pret']
        self.age = mapping['age']

        self.maturity = lambda : self.dataset[self.historical] / self.dataset[self.age]
