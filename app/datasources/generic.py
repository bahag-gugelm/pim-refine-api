from typing import Union, List

class DataSource:
    def search(query: Union[str, List[str]]) -> dict:
        raise NotImplementedError
