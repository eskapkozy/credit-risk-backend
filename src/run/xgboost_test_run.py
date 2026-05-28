from src.run.run_test_Abstraction import RunTestAbstraction


class XgboostTestRun(RunTestAbstraction):

    def __init__(self, train_map: dict = None, test_map: dict = None, val_map: dict = None, config: dict = None,config_path: str = None):
        super().__init__(train_map, test_map, val_map, config, config_path)

