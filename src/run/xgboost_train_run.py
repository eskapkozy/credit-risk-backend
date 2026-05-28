from src.pipelines.Feature.fearurePipline import FeaturePipline
from src.run.run_abstraction import RunAbstraction
from src.service.artifactManager import  ArtifactType


import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, roc_auc_score, recall_score, precision_score, confusion_matrix, accuracy_score , RocCurveDisplay, PrecisionRecallDisplay
import mlflow
import mlflow.xgboost as xGlogger


class XgboostTrainRun(RunAbstraction):

    def __init__(self, train_map: dict = None, test_map: dict = None, val_map: dict = None, config: dict = None,config_path: str = None):
        super().__init__(train_map, test_map, val_map, config, config_path)



    def _run_train(self):

        # #################
        # Train data transformation
        # #################

        self.featurePipline = FeaturePipline(self._x_train, self._y_train, config=self.config)
        binning_process = self.featurePipline.binning_process

        # get transformed and resampled feature Todo [ create imbalance repport ]
        x_train_resampled = self.featurePipline.x_resampled
        y_train_resampled = self.featurePipline.y_resampled

        # ########################
        # Validation data transformation
        # #######################

        validation_config = self.config.copy()
        validation_config['woe']['persistence'] = self.featurePipline.binning_process

        x_val_transformed = FeaturePipline(self._x_val, y_data=None, state='validation', config=validation_config,binning_process=binning_process).transformed

        y_val = self._y_val



        # ########################
        # Model Parametter
        # #######################

        hyperparameters = self.config['model']['hyperparameters']

        # class weight
        neg = (y_train_resampled == 0).sum()
        pos = (y_train_resampled == 1).sum()
        scale_pos_weight = neg / pos

        # early point
        early_stopping_rounds = hyperparameters['early_stopping_rounds']

        # metric
        eval_metric = hyperparameters['eval_metric']

        # Regularisation params
        regularisation = hyperparameters['regularisation']

        # ########################
        # Run
        # #######################

        with mlflow.start_run(run_name=self.config['run']['name']) as run:
            # model param log
            mlflow.log_params(self.config['model'])

            # model fit + get artifact

            model = XGBClassifier(

                # Regularisation
                max_depth=regularisation['max_depth'],
                min_child_weight=regularisation['min_child_weight'],
                reg_lambda=regularisation['reg_lambda'],
                reg_alpha=regularisation['reg_alpha'],
                subsample=regularisation['subsample'],
                colsample_bytree=regularisation['colsample_bytree'],
                learning_rate=regularisation['learning_rate'],

                # early point
                n_estimators=hyperparameters['n_estimators'],
                early_stopping_rounds=early_stopping_rounds,

                # metric
                eval_metric=eval_metric,



                # class weight
                scale_pos_weight=scale_pos_weight,


            )

            self.model_artifact = model.fit(x_train_resampled, y_train_resampled, eval_set=[(x_val_transformed, y_val)], verbose=True)

            # ########################
            # Validation Prediction
            # #######################

            y_predict = model.predict(x_val_transformed)
            y_proba = model.predict_proba(x_val_transformed)[:, 1]

            # ########################
            # Metric  ( F1 - RECALL - ROC - AUC - GINI
            # #######################

            # est-ce que le model discrimine bien ?
            roc_auc = roc_auc_score(y_val, y_proba)
            gini = 2 * roc_auc - 1

            # On définit le seuil suivant les contraintes metier
            handeler = self.threshold(y_val, y_proba)

            predicted_new = handeler[3]

            confusion_mtx = confusion_matrix(y_val, predicted_new)
            tn, fp, fn, tp = confusion_mtx.ravel()

            accuracy = accuracy_score(y_val, predicted_new)

            recall = handeler[0]

            precision = handeler[1]

            f1 = handeler[2]

            # ########################
            #  Log and Persiste
            # #######################

            # metric log
            mlflow.log_metrics({
                'chosen_threshold': handeler[4],
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

            # model artefact  + pipline report
            self.log_model_artifact(self.model_artifact)
            self.log_feature_artifact(self.featurePipline)
            self.log_roc_fig(y_data=y_val, y_proba=y_proba)
            self.log_precision_recall_fig(y_data=y_val, y_prob=y_proba)

        return None






    # =========================
    # HANDLE EVALUATION METRICS
    # =========================

    """
        Seuil de prédiction 26%

    """

    def threshold(self, y_data, y_proba):

        threshold = np.arange(0.1, 0.99, 0.01)
        best_recall = 0
        chosen_threshold = 0
        predicted_new = 0
        best_f1 = 0
        best_precision = 0

        for t in threshold:
            y_pred = (y_proba >= t).astype(int)
            r = recall_score(y_data, y_pred)
            p = precision_score(y_data, y_pred)
            f1 = f1_score(y_data, y_pred)

            if r >= 0.90 and p >= 0.35 and f1 > best_f1:
                best_f1 = f1
                chosen_threshold = t
                predicted_new = y_pred
                best_recall = r
                best_precision = p

        return best_recall, best_precision, best_f1, predicted_new, chosen_threshold

    # =========================
    # PLOTS
    # =========================

    def log_roc_fig(self, y_data, y_proba):

        fig_roc, roc_ax = plt.subplots()
        RocCurveDisplay.from_predictions(y_data, y_proba, ax=roc_ax, name='Xgboost')
        roc_ax.set_title('ROC Curve')
        mlflow.log_figure(fig_roc, 'plots/roc_curve.png')
        plt.close(fig_roc)

    def log_precision_recall_fig(self, y_data, y_prob):

        fig_p, prl_ax = plt.subplots()
        PrecisionRecallDisplay.from_predictions(y_data, y_prob, ax=prl_ax, name='Xgboost')
        prl_ax.set_title('Precision-Recall Curve')
        mlflow.log_figure(fig_p, 'plots/precision_recall_curve.png')
        plt.close(fig_p)

    # =========================
    # ARTIFACT
    # =========================

    def log_model_artifact(self, model_fit):

        # native MLflow logging ( realiser par le Artifact manager )

        self._artifactmanager.log(

            obj=model_fit,
            name='model_fit',
            artifact_type=ArtifactType.PKL
        )

    def log_feature_artifact(self, featurePipline: FeaturePipline):

        self._artifactmanager.log(
            obj=featurePipline.binning_process,
            name='binning_process',
            artifact_type=ArtifactType.PKL
        )

        self._artifactmanager.log(
            obj=featurePipline.woe_iv_report,
            name='woe_iv_report',
            artifact_type=ArtifactType.JSON
        )

        self._artifactmanager.log_woeT0_json(
            obj=featurePipline.woe_table,
            name='woe_table'
        )

        self._artifactmanager.log(
            obj=featurePipline.corr_and_woe_selection_report,
            name='corr_and_woe_selection_report',
            artifact_type=ArtifactType.JSON
        )
