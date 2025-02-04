from typing import Dict, List, Union

JsonType = Union[int, float, str, bool, List["JsonType"], Dict[str, "JsonType"], None]
Json = Dict[str, JsonType]
