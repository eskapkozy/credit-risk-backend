from mlflow.models.cli import predict

from src.pipelines.Feature.fearurePipline import FeaturePipline
from src.run.run_abstraction import RunAbstraction

import numpy as np
import matplotlib.pyplot as plt
import mlflow
import mlflow.sklearn
from sklearn.metrics import f1_score, roc_auc_score, recall_score, precision_score, confusion_matrix, accuracy_score , RocCurveDisplay, PrecisionRecallDisplay




class LogistiqueRegressionTestRun(RunAbstraction):

    def __init__(self,   train_map : dict = None,test_map: dict = None, val_map: dict = None, config : dict = None, config_path : str = None):
        super().__init__(train_map, test_map, val_map, config, config_path)





        self._run_artifact_path = self.config['mlflow']['run_artifact_path']


    def _run_test(self):


        # #################
        # Load Artifact
        # #################

        binning_process, model_fit = self._load_data()

        # ########################
        # Train data transformation
        # #######################

        self.featurePipline = FeaturePipline(self._x_test, self._y_test, config=self.config,binning_process=binning_process)

        x_transformed = self.featurePipline.transformed
        y_test = self._y_test

        # ########################
        # Model Parameter
        # #######################

        # max_iter = int(self.configs['model']['max_iter'])
        # class_weight = self.configs['model']['class_weight']

        #hyperparameters = self.configs['model']['hyperparameters']

        # ########################
        # Run
        # #######################

        with mlflow.start_run(run_name=self.config['run']['name']):

            # model param log
            mlflow.log_params(self.config['model'])


            # ############
            # Test Prediction
            # ############

            y_pred = model_fit.predict(x_transformed)
            y_prob = model_fit.predict_proba(x_transformed)[:,1]


            # ############
            # Test Metrics  ( F1 - RECALL - ROC - AUC - GINI
            # ############

            # Est-ce que le model discrimine bien ?
            roc_auc = roc_auc_score(y_test, y_prob)
            gini = 2*roc_auc - 1



            # Appliquer le seuil est metrique trouver en train
            recall , precision , f1 , predicted_new , threshold = self.threshold(y_test, y_prob)

            confusion_mtx = confusion_matrix(y_test, predicted_new)
            tn, fp, fn, tp = confusion_mtx.ravel()

            accuracy = accuracy_score(y_test, predicted_new)





            # ########################
            #  Log and Persiste
            # #######################

            # metric log
            mlflow.log_metrics({
                'roc_auc': roc_auc,
                'gini': gini,
                'f1': f1,
                'precision': precision,
                'recall': recall,
                'accuracy': accuracy,
                "true_negative": tn,
                "false_positive": fp,
                "false_negative": fn,
                "true_positive": tp

            })

            self._log_roc_fig(y_test, y_prob)
            self._log_precision_recall_fig(y_test, y_prob)

        return None





    """
        Appliquer le seuil est metrique trouver en train
    """
    def threshold(self, y_data,y_proba):

        threshold = self.config['evaluation']['threshold']
        recall = self.config['evaluation']['recall_threshold']
        precision = self.config['evaluation']['precision_threshold']
        f1 = self.config['evaluation']['f1_threshold']

        predicted_new = (y_proba >= threshold).astype(int)

        return recall , precision , f1 , predicted_new , threshold








    # ########################
    #  Persiste
    # #######################


    def y_true(self):
        return self._y_test



    def _load_data(self):

        run_id = self.config['mlflow']['run_artifact_path']['run_id']
        binning_config = self._run_artifact_path['binning_process']
        model_fit_config = self._run_artifact_path['model_fit']

        config = [binning_config, model_fit_config]

        return self._artifactmanager.load_All(run_id = run_id,configList=config)






        # =========================
        # PLOTS
        # =========================

    def _log_roc_fig(self, y_data, y_proba):

        fig_roc, roc_ax = plt.subplots()
        RocCurveDisplay.from_predictions(y_data, y_proba, ax=roc_ax, name='Logistique Regression')
        roc_ax.set_title('ROC Curve')
        mlflow.log_figure(fig_roc, 'plots/roc_curve.png')
        plt.close(fig_roc)

    def _log_precision_recall_fig(self, y_data, y_prob):



        fig_p, prl_ax = plt.subplots()
        PrecisionRecallDisplay.from_predictions(y_data, y_prob, ax=prl_ax, name= self.config['model']['name'])
        prl_ax.set_title('Precision-Recall Curve')
        mlflow.log_figure(fig_p, 'plots/Test_precision_recall_curve.png')
        plt.close(fig_p)