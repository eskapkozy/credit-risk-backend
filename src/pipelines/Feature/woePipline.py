import pandas as pd
import sklearn
from attr.filters import exclude
from optbinning import OptimalBinning, BinningProcess




class WoePipline():

    def __init__(self,x_data : pd.DataFrame ,y_data  : pd.Series = None ,state: str = 'run', config: dict = None,binning_process : BinningProcess = None):

        self.x_data = x_data
        self.y_data = y_data

        self.state = state
        self.config = config

        self.qData = self.x_data.select_dtypes(exclude=['object']).columns.tolist()
        self.categoriel = self.x_data.select_dtypes(include=['object']).columns.tolist()
        self.variable_names = self.qData + self.categoriel



        self.iv_thresold = self.config['iv_threshold']

        self.tranform_metric = self.config['metric']



        # IMPORTANT
        if binning_process is not None:
            self.capturedFit = binning_process
        else:
            self.capturedFit = self._fit()





    def _fit(self):


        bp = BinningProcess(variable_names=self.x_data.columns.tolist(),categorical_variables=self.categoriel, selection_criteria={'iv': {"min": self.iv_thresold}})
        bp = bp.fit(self.x_data, self.y_data)

        return bp


    '''
    en presensence de paramettre recuperation des metadonees du fit depuis une db
    '''
    def transform(self):

        if self.state == 'run' :
            bp = self.capturedFit

            if bp is None:
                raise RuntimeError(
                    "capturedFit n'est pas  initialized. You must call fit() before transform()."
                )

            if not hasattr(bp, "transform"):
                raise TypeError(
                    f" Le capturedFit  de type {type(bp).__name__} n'applique pas de method 'transform' ."
                )

            return bp.transform(self.x_data, metric= self.tranform_metric)
        else:
            bp = self.capturedFit

            if bp is None:
                raise RuntimeError(
                    "capturedFit n'est pas  initialized. You must call fit() before transform()."
                )

            if not hasattr(bp, "transform"):
                raise TypeError(
                    f" Le capturedFit  de type {type(bp).__name__} n'applique pas de method 'transform' ."
                )

            return bp.transform(self.x_data, metric=self.tranform_metric)



    def table(self):

        tables = {}

        for var in self.qData:

            ob = self.capturedFit.get_binned_variable(var)
            tables[var] = ob.binning_table.build()

        return tables



    def iv_report(self):

        iv_report = {}


        for var in self.selected():
            ob = self.capturedFit.get_binned_variable(var)

            table = ob.binning_table.build()

            iv_report[var] = table.loc["Totals", "IV"]


        return pd.DataFrame.from_dict(iv_report, orient="index", columns=["IV"])



    def selection_repport(self):

        df = self.capturedFit.summary()
        selected = self.selected()


        exclude = df[df['selected'] == False]['name'].tolist()

        return {'iv_threshold':self.iv_thresold, 'selected': selected,'rejected': exclude}


    def selected(self):
        df = self.capturedFit.summary()
        return df[df['selected'] == True].name.tolist()
