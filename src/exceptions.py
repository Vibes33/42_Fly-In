class ParsingError(Exception):
    def __init__(self, message: str, line_num: int):
        super().__init__(f"Parsing Error at line {line_num}: {message}")
