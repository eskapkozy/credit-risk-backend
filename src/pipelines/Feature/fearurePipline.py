from src.service.file_maker import FileMaker


from src.pipelines.Feature.capacityPrudential import Prudential_ratios
from src.pipelines.Feature.behavior import Behavior
from src.pipelines.Feature.stability import Stability

from src.pipelines.Feature.woePipline import WoePipline
from imblearn.over_sampling import SMOTE
from src.pipelines.Feature.handleCorreled import handle

import pandas as pd

'''
    Note : pour chaque run ou inference les paramettre sont d'abord definis
'''
class FeaturePipline:

    def __init__(self, x_data : pd.DataFrame, y_data : pd.Series = None, state = 'run', config: dict = None,binning_process = None):



        self.x_data = x_data.copy()
        self.y_data = y_data.copy() if y_data is not None else None

        self.x_resampled = pd.DataFrame
        self.y_resampled = pd.Series

        self.state = state
        self.config = config


        # Construction des features
        self.prudential()
        self.behavior()
        self.stability()

        # correlation befaore handling
        self.correled = pd.DataFrame()

        # Transformation

        self.woe = None

        # woe_artefact
        self.binning_process = binning_process

        self.woe_iv_report = pd.DataFrame
        self.woe_table = pd.DataFrame
        self.corr_and_woe_selection_report = {}






        self.transformed = pd.DataFrame()


        self._init_(binning_process=binning_process)



    def _init_(self,binning_process = None):

        # fit binning process or transform , get Repports

        if binning_process is not None:
            self.woe = WoePipline(self.x_data, self.y_data, state=self.state, config=self.config['woe'],
                                  binning_process=binning_process)

        else:
            self.woe = WoePipline(self.x_data, self.y_data,config=self.config['woe'])
            self.binning_process = self.woe.capturedFit

        woe_transform = self.woe.transform()






        # correlation before handling ( filter )
        self.correled = woe_transform.corr()

        # correlation filter & transformation
        self.transformed = handle(woe_transform).dataset
        corr_handler = handle(woe_transform)


        self._balance()

        #  Repports
        self.woe_iv_report = self.woe.iv_report()
        self.woe_table = self.woe.table()

        self.corr_and_woe_selection_report = {
            'woe':self.woe.selection_repport(),
            'corr':corr_handler.selection_repport(),
            'imbalance': 'Oversampling- SMOTE & ENN'
        }



    def _balance(self):


        if self.state == 'run' and self.y_data is not None:
            smote = SMOTE()
            self.x_resampled, self.y_resampled = smote.fit_resample(self.transformed, self.y_data)





    def prudential(self):
        prudential = Prudential_ratios(self.x_data, {'Revenu': 'person_income', 'Mensualité du prêt': 'loan_amnt', 'Mensualités existantes': None, 'Charges fixes': None})

        '''
        self.dataset['dti'] = prudential.dti()     # manque de donnee
        self.dataset['dsti'] = prudential.dsti()   # manque de donnee
        '''
        self.x_data['residual_income_proxy'] = prudential.residual_income()





    def behavior(self):
        behavior = Behavior(self.x_data, {'historique du pret': 'cb_person_cred_hist_length', 'age': 'person_age'})
        self.x_data['cred_maturity'] = behavior.maturity() * 100

    def stability(self):
        stability = Stability(self.x_data, {'person_emp': 'person_emp_length', 'age': 'person_age'})
        self.x_data['time_work_in_life'] = stability.activity()


    def report_toFile(self):

        filmaker = FileMaker()

        filmaker.create({})



