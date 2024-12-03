from pyobas.signatures.types import MatchTypes
from pyobas.signatures.signature_match import SignatureMatch

class SignatureType:
    def __init__(self, label: str, match_type: str = MatchTypes.MATCH_TYPE_SIMPLE, match_score: int = None):
        self.label = label
        self.match_policy = SignatureMatch(match_type, match_score)

    def make_struct_for_matching(self, data):
        struct = {
            "type": self.match_policy.match_type,
            "data": data,
        }

        if self.match_policy.match_score is not None:
            struct["score"] = self.match_policy.match_score

        return struct