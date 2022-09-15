

class ResponseModel:
    def __init__(self, is_successful: bool, message: str = None, data: any = None):
        self.is_successful = is_successful
        self.message = message
        self.data = data