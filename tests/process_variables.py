from typing import List, Dict, Tuple, Union, Optional
from pydantic import BaseModel, ConfigDict
import datetime


class TestProcessVariables(BaseModel):
    model_config = ConfigDict(extra="allow")

    result: List[str] = []
    empty_str_variable: str = ""
    no_empty_str_variable: str = "test"
    empty_list_variable: List = []
    no_empty_list_variable: List[Union[int, str]] = [1, "test"]
    empty_dict_variable: Dict = {}
    no_empty_dict_variable: Dict[str, str] = {"key": "test"}
    empty_tuple_variable: Tuple = ()
    no_empty_tuple_variable: Tuple[Union[int, str], ...] = (1, "test")
    none_variable: Optional[None] = None
    float_variable: float = 0.09
    int_variable: int = 2
    datetime_variable: datetime.datetime = datetime.datetime(2024, 3, 11)
    starts_with_str_variable: str = "8736 28"
    test_ext_float: float = 1889.9
    str_date: str = "13.03.2024"  # ✅ Added annotation


test = TestProcessVariables().model_dump()
