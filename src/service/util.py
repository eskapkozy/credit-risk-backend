

import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import seaborn as sns
import pandas as pd

from scipy import stats as stats

class Util:


    def __init__(self,dataset:pd.DataFrame, target:str):
        self.dataset = dataset
        self.target = target
        self.cats = self.dataset[self.target].unique().tolist()

        self.contingency_count = lambda  line_index, feature: pd.crosstab(self.dataset[line_index], self.dataset[feature],
                                                                             margins=True)
        self.contingency_effLine = lambda  line_index, feature: pd.crosstab(self.dataset[line_index], self.dataset[feature],
                                                                               margins=True, normalize='all')
        self.contingency_perLine = lambda  line_index, feature: pd.crosstab(self.dataset[line_index], self.dataset[feature],
                                                                               normalize='columns', margins=True)


    def binsFrom_hist(self,feature: str,bins = 20)  -> pd.DataFrame:
        counts, bin_edges = np.histogram(self.dataset[feature], bins=bins)

        df_bins = pd.DataFrame({
            'intervalle': [f"[{bin_edges[i]:.2f} - {bin_edges[i + 1]:.2f}]" for i in range(len(counts))],
            'borne_gauche': bin_edges[:-1],
            'borne_droite': bin_edges[1:],
            'frequence': counts,
            'pct': (counts / counts.sum() * 100).round(2)
        }).sort_values('frequence', ascending=False)

        return df_bins

    def probdensity(self, feature: str, law: str, upper_born, lower_born):
        dist = 0
        if law == 'log-normal':
            shape, loc, scale = stats.lognorm.fit(self.dataset[feature])
            dist = stats.lognorm(shape, loc, scale)
        else:
            mu, sigma = stats.norm.fit(self.dataset[feature])
            dist = stats.norm(mu, sigma)
        return dist.cdf(upper_born) - dist.cdf(lower_born)

    def qcut(self, feature, q = 4, labes=None):
            if labes is None:
                labes = ['FAIBLE', 'MOYEN', 'HAUT', 'FORT']
            if q == None: q = 4
            concat_ = feature +'_TRANCHE'
            x_df = self.dataset.copy()
            x_df[concat_], limit =pd.qcut(x = x_df[feature], q=q, labels=labes,retbins=True)



            return (x_df,limit)




    ''' Discretisation suivant la regle des quantiles '''

    def qdiscret_proportion(self,  feature, other_feature, q=4, labels = None):

        df,limit = self.qcut( feature, q, labels)

        grouped = (
            df
            .groupby([feature + '_TRANCHE', other_feature])
            .size()
        )

        proportion = (
            grouped
            .groupby(level=0)
            .apply(lambda x: x / x.sum())
            .rename('proportion')
        )

        return (proportion, limit)


    # observer distribution
    def global_view(self, feature: str):
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        sns.histplot(self.dataset, x=feature, ax=axes[0], kde=True, bins=20)
        axes[0].set_title(f'skew: {self.dataset[feature].skew():.2f}')

        sns.boxplot(self.dataset, x=feature, ax=axes[1])
        axes[1].set_title(f'median : {self.dataset[feature].median():.2f}')

        plt.tight_layout()
        plt.show()

    def visualize_cat(self, feature, figsize = None):

        if figsize is None: figsize = (10, 5)
        #d

        fig, axes = plt.subplots(1, 2, figsize=figsize)
        count = self.dataset[feature].value_counts()

        sns.countplot(self.dataset, x=feature, ax=axes[0])
        plt.pie(count, labels=count.index, radius=1.2, autopct='%1.1f%%')
        plt.tight_layout()
        plt.show()

    '''
        Visualisation pour le bivarier
        observation d'un box plot et barplot
    '''

    def box_barPlot(self, target: str, feature: str):

        y_mean = self.dataset.groupby(target)[feature].mean()
        y_median = self.dataset.groupby(target)[feature].median()

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        sns.boxplot(data=self.dataset, x=target, y=feature, hue=target, ax=axes[0])
        axes[0].set_title(
            f'median_Default: {y_median[1]:.2f}   median_NonDefault: {y_median[0]:.2f}'
        )

        sns.barplot(data=self.dataset, x=target, y=feature, hue=target, ax=axes[1])
        axes[1].set_title(
            f'mean_Default: {y_mean[1]:.2f}   mean_NonDefault: {y_mean[0]:.2f}'
        )

        plt.tight_layout()

    '''
                Observer la discretisation par quartil
            '''

    def scatter_of_default_qtl(self, feature:str ,other_feature = None,index = None):

        if other_feature is None: other_feature = self.target
        if index is None: index = ['FAIBLE', 'MOYEN', 'HAUT', 'FORT']

        disc_qt_defaul     = self.qdiscret_proportion(feature,other_feature)[0][:, :, self.cats[1]].values
        disc_qt_no_default = self.qdiscret_proportion(feature,other_feature)[0][:, :, self.cats[0]].values

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))

        sns.stripplot(x= index, y=disc_qt_defaul, linestyles="-", ax=axes[0])
        axes[0].set_title('Default')
        sns.stripplot(x=index, y=disc_qt_no_default, linestyles='-',
                     ax=axes[1])
        axes[1].set_title('NoDefault')
