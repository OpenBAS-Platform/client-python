from typing import List

from pyobas.contracts.contract_config import ContractElement, ContractOutputElement


class ContractBuilder:
    fields: List[ContractElement]
    outputs: List[ContractOutputElement]

    def __init__(self):
        self.fields = []
        self.outputs = []

    def add_fields(self, fields: List[ContractElement]):
        self.fields = self.fields + fields
        return self

    def add_outputs(self, outputs: List[ContractOutputElement]):
        self.outputs = self.outputs + outputs
        return self

    def mandatory(self, element: ContractElement):
        element.mandatory = True
        self.fields.append(element)
        return self

    def optional(self, element: ContractElement):
        element.mandatory = False
        self.fields.append(element)
        return self

    def mandatory_group(self, elements: List[ContractElement]):
        keys: List[str] = list(map(lambda iterable: iterable.key, elements))
        for element in elements:
            element.mandatory = True
            element.mandatoryGroups = keys
            self.fields.append(element)
        return self

    def build_fields(self) -> List[ContractElement]:
        return self.fields

    def build_outputs(self) -> List[ContractOutputElement]:
        return self.outputs
