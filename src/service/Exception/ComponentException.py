class WoeLoadException(Exception):
    def __init__(self, message=None, context=None):
        if message is None:
            message = "WOE load error: configuration or persistence is inconsistent"

        super().__init__(message)

        self.context = context