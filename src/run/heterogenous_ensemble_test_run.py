from sklearn.ensemble import StackingClassifier

from src.run.run_test_Abstraction import RunTestAbstraction


class HeterogeneousEnsembleTestRun(RunTestAbstraction):

    def __init__(self, train_map: dict = None, test_map: dict = None, val_map: dict = None, config: dict = None,config_path: str = None):
        super().__init__(train_map, test_map, val_map, config, config_path)

        self.stacking_weights = None
        self.base_learners = None
        self.meta_learner = None
        self.contributions = None

    def _load_data(self):
        run_id = self.config['mlflow']['run_artifact_path']['run_id']

        config = [
            self._run_artifact_path['binning_process'],
            self._run_artifact_path['model_fit'],
            self._run_artifact_path['stacking_weights'],
        ]

        artifacts = self._artifactmanager.load_All(run_id=run_id, configList=config)

        binning_process = artifacts[0]
        model_fit = self._reconstruct_model(artifacts[1], artifacts[2])

        return binning_process, model_fit



    def _reconstruct_model(self, ensemble, stacking_weights):
        ensemble.stacking_weights_ = stacking_weights

        self.model = ensemble
        self.base_learners = ensemble.named_estimators_
        self.meta_learner = ensemble.final_estimator_
        self.stacking_weights = stacking_weights  # déjà passé en paramètre

        return ensemble