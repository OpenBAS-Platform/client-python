import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict

from pyobas import utils
from pyobas.contracts.contract_utils import ContractCardinality, ContractVariable
from pyobas.contracts.variable_helper import VariableHelper


class SupportedLanguage(str, Enum):
    fr: str = "fr"
    en: str = "en"


class ContractFieldType(str, Enum):
    Text: str = "text"
    Number: str = "number"
    Tuple: str = "tuple"
    Checkbox: str = "checkbox"
    Textarea: str = "textarea"
    Select: str = "select"
    Article: str = "article"
    Challenge: str = "challenge"
    DependencySelect: str = "dependency-select"
    Attachment: str = "attachment"
    Team: str = "team"
    Expectation: str = "expectation"
    Asset: str = "asset"
    AssetGroup: str = "asset-group"
    Payload: str = "payload"


class ContractOutputType(str, Enum):
    Text: str = "text"
    Number: str = "number"
    Port: str = "port"
    PortsScan: str = "portscan"
    IPv4: str = "ipv4"
    IPv6: str = "ipv6"
    CVE: str = "cve"


class ExpectationType(str, Enum):
    text: str = "TEXT"
    document: str = "DOCUMENT"
    article: str = "ARTICLE"
    challenge: str = "CHALLENGE"
    manual: str = "MANUAL"
    prevention: str = "PREVENTION"
    detection: str = "DETECTION"
    vulnerability: str = "VULNERABILITY"


@dataclass
class Expectation:
    expectation_type: ExpectationType
    expectation_name: str
    expectation_description: str
    expectation_score: int
    expectation_expectation_group: bool


@dataclass
class LinkedFieldModel:
    key: str
    type: ContractFieldType


@dataclass
class ContractElement(ABC):
    key: str
    label: str
    type: str = field(default="", init=False)
    mandatoryGroups: List[str] = field(default_factory=list)
    mandatoryConditionFields: List[str] = field(default_factory=list)
    mandatoryConditionValues: Dict[str, any] = field(default_factory=list)
    visibleConditionFields: List[str] = field(default_factory=list)
    visibleConditionValues: Dict[str, any] = field(default_factory=list)
    linkedFields: List[str] = field(default_factory=list)
    mandatory: bool = False
    readOnly: bool = False

    @property
    @abstractmethod
    def get_type(self) -> str:
        pass

    def __post_init__(self):
        self.type = self.get_type


@dataclass
class ContractCardinalityElement(ContractElement, ABC):
    cardinality: str = ContractCardinality.One
    defaultValue: List[str] = field(default_factory=list)


@dataclass
class ContractOutputElement(ABC):
    type: str
    field: str
    labels: List[str]
    isFindingCompatible: bool
    isMultiple: bool


@dataclass
class ContractConfig:
    type: str
    expose: bool
    label: dict[SupportedLanguage, str]
    color_dark: str
    color_light: str


@dataclass
class Contract:
    contract_id: str
    label: dict[SupportedLanguage, str]
    fields: List[ContractElement]
    outputs: List[ContractOutputElement]
    config: ContractConfig
    manual: bool
    variables: List[ContractVariable] = field(
        default_factory=lambda: [
            VariableHelper.user_variable(),
            VariableHelper.exercise_variable(),
            VariableHelper.team_variable(),
        ]
        + VariableHelper.uri_variables()
    )
    contract_attack_patterns_external_ids: List[str] = field(default_factory=list)
    is_atomic_testing: bool = True
    platforms: List[str] = field(default_factory=list)

    def add_attack_pattern(self, var: str):
        self.contract_attack_patterns_external_ids.append(var)

    def add_variable(self, var: ContractVariable):
        self.variables.append(var)


@dataclass
class ContractTeam(ContractCardinalityElement):
    @property
    def get_type(self) -> str:
        return ContractFieldType.Team.value


@dataclass
class ContractText(ContractCardinalityElement):

    defaultValue: str = ""

    @property
    def get_type(self) -> str:
        return ContractFieldType.Text.value


def prepare_contracts(contracts):
    return list(
        map(
            lambda c: {
                "contract_id": c.contract_id,
                "contract_labels": c.label,
                "contract_attack_patterns_external_ids": c.contract_attack_patterns_external_ids,
                "contract_content": json.dumps(c, cls=utils.EnhancedJSONEncoder),
                "contract_platforms": c.platforms,
            },
            contracts,
        )
    )


@dataclass
class ContractTuple(ContractCardinalityElement):
    def __post_init__(self):
        super().__post_init__()
        self.cardinality = ContractCardinality.Multiple

    attachmentKey: str = None
    contractAttachment: bool = attachmentKey is not None
    tupleFilePrefix: str = "file :: "

    @property
    def get_type(self) -> str:
        return ContractFieldType.Tuple.value


@dataclass
class ContractTextArea(ContractCardinalityElement):

    defaultValue: str = ""
    richText: bool = False

    @property
    def get_type(self) -> str:
        return ContractFieldType.Textarea.value


@dataclass
class ContractCheckbox(ContractElement):

    defaultValue: bool = False

    @property
    def get_type(self) -> str:
        return ContractFieldType.Checkbox.value


@dataclass
class ContractAttachment(ContractCardinalityElement):

    @property
    def get_type(self) -> str:
        return ContractFieldType.Attachment.value


@dataclass
class ContractExpectations(ContractCardinalityElement):
    cardinality = ContractCardinality.Multiple
    predefinedExpectations: List[Expectation] = field(default_factory=list)

    @property
    def get_type(self) -> str:
        return ContractFieldType.Expectation.value


@dataclass
class ContractSelect(ContractCardinalityElement):

    choices: dict[str, str] = None

    @property
    def get_type(self) -> str:
        return ContractFieldType.Select.value


@dataclass
class ContractAsset(ContractCardinalityElement):

    @property
    def get_type(self) -> str:
        return ContractFieldType.Asset.value


@dataclass
class ContractAssetGroup(ContractCardinalityElement):

    @property
    def get_type(self) -> str:
        return ContractFieldType.AssetGroup.value


@dataclass
class ContractPayload(ContractCardinalityElement):

    @property
    def get_type(self) -> str:
        return ContractFieldType.Payload.value
