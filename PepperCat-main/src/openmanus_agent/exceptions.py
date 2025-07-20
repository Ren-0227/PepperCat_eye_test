class ToolError(Exception):
    def __init__(self, message):
        self.message = message
class OpenManusError(Exception):
    pass
class TokenLimitExceeded(OpenManusError):
    pass 