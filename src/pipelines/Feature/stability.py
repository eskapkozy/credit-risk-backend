import pandas as pd

class Stability:

    def __init__(self, dataset: pd.DataFrame, mapping: dict):
        self.dataset = dataset.copy()
        self.mapping = mapping

        self.person_emp = mapping['person_emp']
        self.age = mapping['age']

        self.activity = lambda : self.dataset[self.person_emp] / self.dataset[self.age]