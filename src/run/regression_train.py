import pandas as pd
import matplotlib.pyplot as plt
import mlflow.sklearn
import yaml
from sklearn.linear_model import LogisticRegression



from src.pipelines.Feature.fearurePipline import FeaturePipline
from src.service.artifactManager import ArtifactManager, ArtifactType


from sklearn.metrics import f1_score, roc_auc_score, recall_score, precision_score, confusion_matrix, accuracy_score , RocCurveDisplay, PrecisionRecallDisplay


class Regression_logistique_baseline():

    def __init__(self,   train_map : dict ,test_map: dict = None, val_map: dict = None, config : dict = None, config_path : str = None):


        self.x_train    = train_map['x_train']
        self.y_train    = train_map['y_train']

        self.x_test     = test_map['x_test']            if test_map is not None else None
        self.y_test     = test_map['y_test']            if test_map is not None else None

        self.x_val      = val_map['x_val']               if val_map is not None else None
        self.y_val      = val_map['y_val']               if val_map is not None else None



        self.config_path = config_path
        self.config = config if config_path is None else self._getConfig()

        # self._imbalance = configs['imbalance']


        mlflow.set_tracking_uri("http://localhost:5000")
        mlflow.set_experiment("classification")

        self.featurePipline = None

        # Artifact
        self.model_artifact = None
        self.artifactmanager = ArtifactManager()





    def run(self):


        # ########################
        # Train data transformation
        # #######################


        self.featurePipline = FeaturePipline(self.x_train, self.y_train,config = self.config)

        # get transformed and resampled feature Todo [ create imbalance repport ]
        x_train_resampled = self.featurePipline.x_resampled
        y_train_resampled = self.featurePipline.y_resampled

        # ########################
        # Validation data transformation
        # #######################

        validation_config = self.config.copy()
        validation_config['woe']['persistence'] = self.featurePipline.binning_process

        x_val_transformed = FeaturePipline(self.x_val, y_data=None , state= 'validation', config=validation_config).transformed
        y_val = self.y_val


        # ########################
        # Model Parametter
        # #######################

        max_iter = int( self.config['model']['max_iter'] )

        # ########################
        # Run
        # #######################

        with mlflow.start_run(run_name=self.config['run']['name']) as run :
            print("Artifact URI:", run.info.artifact_uri)

            # model param log
            mlflow.log_params(self.config['model'])

            # model fit + get artefact
            model = LogisticRegression(max_iter = max_iter, class_weight='balanced')
            self.model_artifact = model.fit(x_train_resampled, y_train_resampled)



            # ########################
            # Validation Prediction
            # #######################

            y_predict   = model.predict(x_val_transformed)
            y_proba     = model.predict_proba(x_val_transformed)[:,1]

            # ########################
            # Metric  ( F1 - RECALL - ROC - AUC - GINI
            # #######################

            roc_auc         = roc_auc_score(y_val,y_proba)
            f1              = f1_score(y_val,y_predict)
            precision       = precision_score(y_val,y_predict)
            recall          = recall_score(y_val,y_predict)
            accuracy        = accuracy_score(y_val,y_predict)
            confusion_mtx   = confusion_matrix(y_val,y_predict)

            tn, fp, fn, tp = confusion_mtx.ravel()


            # ########################
            #  Log and Persiste
            # #######################

            # metric log
            mlflow.log_metrics({
                'roc_auc'       : roc_auc,
                'f1'            : f1,
                'precision'     : precision,
                'recall'        : recall,
                'accuracy'      : accuracy,
                "true_negative" : tn,
                "false_positive": fp,
                "false_negative": fn,
                "true_positive" : tp

            })



            # model artefact  + pipline report
            self.log_model_artifact(self.model_artifact)
            self.log_feature_artifact(self.featurePipline)
            self.log_roc_fig(y_data=y_val, y_proba=y_proba)
            self.log_precision_recall_fig(y_data=y_val, y_prob=y_proba)




    # =========================
    # PLOTS
    # =========================

    def log_roc_fig(self,y_data, y_proba):

        fig_roc , roc_ax = plt.subplots()
        RocCurveDisplay.from_predictions(y_data, y_proba,ax = roc_ax, name='Logistique Regression')
        roc_ax.set_title('ROC Curve')
        mlflow.log_figure(fig_roc,'plots/roc_curve.png')
        plt.close(fig_roc)

    def log_precision_recall_fig(self,y_data,y_prob):

        fig_p , prl_ax = plt.subplots()
        PrecisionRecallDisplay.from_predictions(y_data, y_prob,ax = prl_ax, name='Logistique Regression')
        prl_ax.set_title('Precision-Recall Curve')
        mlflow.log_figure(fig_p,'plots/precision_recall_curve.png')
        plt.close(fig_p)


    # =========================
    # ARTIFACT
    # =========================

    def log_model_artifact(self, model_fit):

        # native MLflow logging ( realiser par le Artifact manager )

        self.artifactmanager.log(

            obj = model_fit,
            name = 'model_fit',
            artifact_type= ArtifactType.PKL
        )



    def log_feature_artifact(self, featurePipline: FeaturePipline):



        self.artifactmanager.log(
            obj=featurePipline.binning_process,
            name='binning_process',
            artifact_type= ArtifactType.PKL
        )

        self.artifactmanager.log(
            obj=featurePipline.woe_iv_report,
            name='woe_iv_report',
            artifact_type= ArtifactType.JSON
        )

        self.artifactmanager.log_woeT0_json(
            obj=featurePipline.woe_table,
            name='woe_table'
        )


        self.artifactmanager.log(
            obj=featurePipline.corr_and_woe_selection_report,
            name='corr_and_woe_selection_report',
            artifact_type= ArtifactType.JSON
        )

    def _getConfig(self):

        config = {}
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config






