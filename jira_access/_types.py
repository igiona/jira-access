from typing import Dict, List, Union

JsonType = Union[None, int, float, str, bool, List["JsonType"], Dict[str, "JsonType"]]
Json = Dict[str, JsonType]
