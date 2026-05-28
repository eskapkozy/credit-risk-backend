import pandas as pd

class handle:

    def __init__(self,dataset: pd.DataFrame, threshold = 0.07):
        self.dataset = dataset.copy()
        self.correled = ['residual_income_proxy', 'time_work_in_life','loan_int_rate']

        self.threshold = threshold

        self.dropCorreled()

    def dropCorreled(self):
        self.dataset = self.dataset.drop(self.correled, axis=1)

    def selection_repport(self):

        return {'correlation_thresold':self.threshold, 'rejected': self.correled}