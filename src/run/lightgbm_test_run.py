from src.run.run_test_Abstraction import RunTestAbstraction


class LightgbmTestRun(RunTestAbstraction):
    def __init__(self, test_map: dict = None, config: dict = None, config_path: str = None):
        super().__init__(test_map=test_map, config= config, config_path=config_path)

