from hs.entities.base_entity import BaseEntity
from typing import Dict, List, Optional, Union
from hydrosdk.signature import ModelSignature, ModelField

class Field(BaseEntity):
    shape: Union[List[int], str]
    type: str
    profile: str

class Contract(BaseEntity):
    name: Optional[str]
    inputs: Dict[str, Field]
    outputs: Dict[str, Field]

    def to_proto(self):
        #todo: implement the conversion
        pass
    