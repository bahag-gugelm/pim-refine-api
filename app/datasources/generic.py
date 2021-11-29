from typing import Union, List

class DataSource:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def search(query: Union[str, List[str]]) -> dict:
        raise NotImplementedError
