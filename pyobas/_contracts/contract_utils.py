from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ContractCardinality(str, Enum):
    One: str = "1"
    Multiple: str = "n"


class VariableType(str, Enum):
    String: str = "String"
    Object: str = "Object"


@dataclass
class ContractVariable:
    key: str
    label: str
    type: VariableType
    cardinality: ContractCardinality
    children: List["ContractVariable"] = field(default_factory=list)
