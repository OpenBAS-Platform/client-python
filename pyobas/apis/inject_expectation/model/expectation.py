from enum import Enum
from typing import List
from uuid import UUID

from pydantic import BaseModel
from thefuzz import fuzz

from pyobas.signatures.signature_type import SignatureType
from pyobas.signatures.types import MatchTypes, SignatureTypes


class ExpectationTypeEnum(str, Enum):
    Detection = "DETECTION"
    Prevention = "PREVENTION"
    Other = "other"

    @classmethod
    def _missing_(cls, value):
        return cls.Other


class ExpectationSignature(BaseModel):
    type: SignatureTypes
    value: str


class Expectation(BaseModel):
    inject_expectation_id: UUID
    inject_expectation_signatures: List[ExpectationSignature]

    success_label: str = "Success"
    failure_label: str = "Failure"

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.__api_client = kw["api_client"]

    def update(self, success, sender_id, metadata):
        self.__api_client.update(
            self.inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": (self.success_label if success else self.failure_label),
                "is_success": success,
                "metadata": metadata,
            },
        )

    def match_alert(self, relevant_signature_types: list[SignatureType], alert_data):
        relevant_expectation_signatures = [
            signature
            for signature in self.inject_expectation_signatures
            if signature.type in [type.label for type in relevant_signature_types]
        ]
        if not any(relevant_expectation_signatures):
            return False

        for relevant_expectation_signature in relevant_expectation_signatures:
            if not (
                alert_signature_for_type := alert_data.get(
                    relevant_expectation_signature.type.value
                )
            ):
                return False

            if alert_signature_for_type[
                "type"
            ] == MatchTypes.MATCH_TYPE_FUZZY and not self.match_fuzzy(
                alert_signature_for_type["data"],
                relevant_expectation_signature.value,
                alert_signature_for_type["score"],
            ):
                return False
            if alert_signature_for_type[
                "type"
            ] == MatchTypes.MATCH_TYPE_SIMPLE and not self.match_simple(
                alert_signature_for_type["data"], relevant_expectation_signature.value
            ):
                return False

        return True

    @staticmethod
    def match_fuzzy(tested: list[str], target: str, threshold: int):
        actual_tested = [tested] if isinstance(tested, str) else tested
        for value in actual_tested:
            ratio = fuzz.ratio(value, target)
            if ratio >= threshold:
                return True
        return False

    @staticmethod
    def match_simple(tested: list[str], target: str):
        return target in tested


class DetectionExpectation(Expectation):
    success_label: str = "Detected"
    failure_label: str = "Not Detected"


class PreventionExpectation(Expectation):
    success_label: str = "Prevented"
    failure_label: str = "Not Prevented"
