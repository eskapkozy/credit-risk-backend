import pandas as pd
from pandas.core.interchange.dataframe_protocol import DataFrame


class Prudential_ratios:



    def __init__(self, dataset: pd.DataFrame, mapping: dict):
        self.dataset = dataset.copy()

        self.revenu = self.dataset[mapping['Revenu']] if mapping['Revenu'] else None


        self.mensualite_pret = mapping['Mensualité du prêt']


        self.mensualites_existantes = mapping['Mensualités existantes']
        self.charges_fixes = mapping['Charges fixes']

        self.data = lambda : {'dti': self.dti(), 'dsti': self.dsti(), 'residual_income': self.residual_income(), 'dti_quality': self.dti_quality()}

    def total_mensualites(self):
        parts = []

        if self.mensualites_existantes:
            parts.append(self.dataset[self.mensualites_existantes].sum(axis=1))

        if self.mensualite_pret :
            parts.append(self.dataset[self.mensualite_pret])

        return sum(parts) if parts else 0  #  fallback à 0



    def total_charges(self):
        if self.charges_fixes:
            return self.dataset[self.charges_fixes].sum(axis=1)
        return 0  # 🔥 fallback à 0


    def dti(self):
        if self.revenu is None:
            return None
        return (self.total_mensualites() + self.total_charges()) / self.revenu

    def dsti(self):
        if self.revenu is None or self.mensualite_pret is None:
            return None
        return self.dataset[ self.mensualite_pret ] / self.revenu

    def residual_income(self):
        if self.revenu is None:
            return None
        return self.revenu - self.total_charges() - self.total_mensualites()


    def dti_quality(self):
        score = 0
        if self.mensualites_existantes: score += 1
        if self.mensualite_pret : score += 1
        if self.charges_fixes: score += 1
        return score