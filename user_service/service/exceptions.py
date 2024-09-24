class MissingRequiredFields(Exception):
    def __init__(self, fields: list[str]):
        self.fields = fields
