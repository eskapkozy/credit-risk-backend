
import mlflow.sklearn
import yaml

from pathlib import Path

from src.pipelines.Feature.fearurePipline import FeaturePipline
from src.service.artifactManager import ArtifactManager, ArtifactType

class RunAbstraction:

    def __init__(self,   train_map : dict = None,test_map: dict = None, val_map: dict = None, config : dict = None, config_path : str = None):

        self.config_path = config_path
        self.config = config if config_path is None else self._getConfig()
        self._is_train = self.config['run']['is_train']

        self._isvalideMap(train_map, val_map, test_map)





        self._x_train = None
        self._y_train = None

        self._x_test = None
        self._y_test = None

        self._x_val = None
        self._y_val = None


        if self._is_train:
            self._x_train = train_map['x_train']
            self._y_train = train_map['y_train']

            self._x_val = val_map['x_val'] if val_map is not None else None
            self._y_val = val_map['y_val'] if val_map is not None else None

        else:
            self._x_test = test_map['x_test'] if test_map is not None else None
            self._y_test = test_map['y_test'] if test_map is not None else None



        # self._imbalance = configs['imbalance']


        mlflow.set_tracking_uri(    self.config['mlflow']['tracking_uri'])
        mlflow.set_experiment(      self.config['mlflow']['experiment_name'])

        self.featurePipline = None

        # Artifact
        self._model_artifact = None
        self._artifactmanager = ArtifactManager()



        # evaluation metrique
        self._chosen_threshold = None
        self._best_recall = None
        self._best_precision = None
        self._best_f1 = None






    def run(self):

        if self._is_train:
            self._run_train()
        else:
            self._run_test()







    def _run_test(self):
        return  None

    def _run_train(self):
        return None


    def _load_data(self):
        pass

    def _getConfig(self):

        config = {}
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)

        return config


    def _setEvaluationMetrics(self, chosen_threshold, best_recall, best_precision, best_f1):
        self._chosen_threshold = chosen_threshold
        self._best_recall = best_recall
        self._best_precision = best_precision
        self._best_f1 = best_f1

    def save_evaluation_metrics(self, test_config_path: str):
        """
        Écrit les métriques du dernier run directement dans le fichier de configs test.
        À appeler manuellement après validation visuelle des métriques dans MLflow.

        Usage :
            model.run()
            # → vérifier les métriques dans MLflow
            model.save_evaluation_metrics("configs/test_config.yaml")
        """

        # Lire le configs test existant
        path = Path(test_config_path)
        with open(path, "r") as f:
            test_config = yaml.safe_load(f)

        # Écraser uniquement le bloc evaluation
        test_config["evaluation"] = {
            "roc_auc": True,
            "recall": True,
            "precision": True,
            "f1_score": True,
            "confusion_matrix": True,
            "threshold": float(self._chosen_threshold),
            "recall_threshold": float(self._best_recall),
            "precision_threshold": float(self._best_precision),
            "f1_threshold": float(self._best_f1),
        }

        with open(path, "w") as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ Métriques sauvegardées dans {path}")

    # todo remplecer le  valide mapp par de vrai exception
    def _isvalideMap(self, train_map, val_map, test_map):

        if self._is_train == False and train_map is not None:
            raise ValueError("Vous avez fournis un mapping de Train pendant un Test Run")

        if self._is_train == False and val_map is not None:
            raise ValueError("Vous avez fournis un mapping de validation pendant un Test Run")

        if self._is_train and test_map is not None:
            raise ValueError("Vous avez fournis un mapping de test pendant un train Run")







