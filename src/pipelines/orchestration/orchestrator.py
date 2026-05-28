import mlflow

from src.pipelines.Feature.fearurePipline import FeaturePipline
from src.service.artifactManager import ArtifactManager



class Orchestrator:
    def __init__(self, mlflow_config: dict,model_config: dict, request_data):

        self._model_config = model_config
        self._state = model_config['state']

        self._x_data = request_data


        self._mlflow_config = mlflow_config
        self._artifactmanager = ArtifactManager()



        mlflow.set_tracking_uri(self._mlflow_config['tracking_uri'])
        mlflow.set_experiment(self._mlflow_config['experiment_name'])


    # todo: add logging
    def orchestrate(self):


        # ##############################
        # Load model
        # ##############################

        binning_process, model_fit = self.load_model()


        # ########################
        #  data transformation
        # #######################

        featurePipline = FeaturePipline(x_data= self._x_data, y_data=None,state=self._state, config=self._model_config,binning_process=binning_process)
        x_transformed = featurePipline.transformed

        # #############
        # Prediction from x_transformed
        # #############

        y_prob = model_fit.predict_proba(x_transformed)[:, 1]



        return y_prob








    def load_model(self):

        def _reconstruct_model( ensemble, stacking_weights):
            ensemble.stacking_weights_ = stacking_weights

            return ensemble


        def _load_data():
            run_id = self._mlflow_config['run_id']

            config = [
                self._mlflow_config['binning_process'],
                self._mlflow_config['model_fit'],
                self._mlflow_config['stacking_weights'],
            ]

            artifacts = self._artifactmanager.load_All(run_id=run_id, configList=config)

            binning_process = artifacts[0]
            model_fit = _reconstruct_model(artifacts[1], artifacts[2])

            return binning_process, model_fit

        return  _load_data()