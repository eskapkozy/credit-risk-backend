import math

import numpy as np
import pandas as pd
import pingouin as pg

from scipy import stats
from scipy.stats import chi2_contingency


class StatTest:
    def __init__(self, dataset,target:str):
        self.dataset = dataset
        self.target = target
        self.cats = self.dataset[self.target].unique().tolist()

    def corr_cohen(self,feature:str):
        return self.compute_effectsize(feature),self.compute_ttest(feature)



    def cohen_matrix(self,  limit=0.05):
        features = [
            col for col in self.dataset.columns
            if self.dataset[col].dtype in ['int64', 'float64']

        ]






        info = []

        for feature in features:
            cohen = self.compute_effectsize(feature) if self.compute_ttest(feature) < limit else 0.0
            info.append({'feature': feature, 'cohen': cohen})

        return pd.DataFrame(info).sort_values(by='cohen', ascending=False).reset_index(drop=True)

    '''
                   Test : Significativite
                   Type : Categorielle a deux groupe et quantitative
                   p-value < 0.05 : a moin de 5% chance, la difference des moyen entre les groupe  est significative, aucun hasard 
    '''

    def compute_ttest(self,feature: str):
        g1 = self.dataset[self.dataset[self.target] == self.cats[0]][feature]
        g2 = self.dataset[self.dataset[self.target] == self.cats[1]][feature]

        return stats.ttest_ind(g1, g2)[1]




    '''
                  Test : correlation coefficient
                  TYpe : categorielle et quantitative
                  r < 0.2 : la taille d'effet est faible 
                  Taille d'effet moderer 0.5
                  Taille d'effet forte 0.8
    '''

    def compute_effectsize(self,feature: str):
        g1 = self.dataset[self.dataset[self.target] == self.cats[0]][feature]
        g2 = self.dataset[self.dataset[self.target] == self.cats[1]][feature]

        return math.fabs(pg.compute_effsize(g1, g2, eftype='cohen'))



    def cramer_matrix(self, cat_cols: list, limit=0.05):

        # on definit la fonction de cramer

        def v_cramer(x, y):
            tableau = pd.crosstab(x, y)
            chi2, p_value, dof, _ = chi2_contingency(tableau)
            n = tableau.sum().sum()
            k = min(tableau.shape) - 1
            v = np.sqrt(chi2 / (n * k))
            return v, p_value

        score = []

        for col in cat_cols:
            v, p = v_cramer(self.dataset[col], self.dataset[self.target])
            significativite = p < limit
            score.append({'variable': col, 'score': v, 'p_value': p, 'significativite': significativite})

        score_df = pd.DataFrame(score).sort_values('score', ascending=False)

        candidate = score_df[score_df['significativite'] == True]['variable'].tolist()

        all_cols = candidate + [self.target]

        matrice = pd.DataFrame(index=all_cols, columns=all_cols, dtype='float64')

        # on parcour la matrice pour calculer le v_cramer
        for col1 in all_cols:
            for col2 in all_cols:
                v, p = v_cramer(self.dataset[col1], self.dataset[col2])
                matrice.loc[col1, col2] = v if p < limit else 0.0

        return matrice