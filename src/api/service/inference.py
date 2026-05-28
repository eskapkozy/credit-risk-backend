from src.api.core.mlflow_config import Mlflow_config
from src.api.core.model_config import Model_config
from src.pipelines.orchestration.orchestrator import Orchestrator


class Inference:

    def __init__(self):


        self.mlflow_config = Mlflow_config()
        self._model_config = Model_config()



    def predict(self,request_data, threshold = None):

        _threshold = self._model_config.evaluation['threshold'] if threshold is None else threshold

        orchestrator = Orchestrator(
            mlflow_config=self.mlflow_config.config,
            model_config=self._model_config.config,
            request_data=request_data
        )

        predicted = self.rule(orchestrator.orchestrate(),_threshold)
        y_prob = orchestrator.orchestrate()


        return {
            "prediction": int(predicted.item()),
            "probability": float(y_prob.item()),
            "threshold": float(_threshold),

        }




    def rule(self, prob, threshold):
        return (prob >= threshold).astype(int)



