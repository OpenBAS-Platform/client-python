from pyobas.signatures.signature_match import SignatureMatch
from pyobas.signatures.types import MatchTypes, SignatureTypes


class SignatureType:
    def __init__(
        self,
        label: SignatureTypes,
        match_type: MatchTypes = MatchTypes.MATCH_TYPE_SIMPLE,
        match_score: int = None,
    ):
        self.label = label
        self.match_policy = SignatureMatch(match_type, match_score)

    # provided some `data`, formats a dictionary specifying the matching
    # policy to use by the helper to match expected signatures (from expectations)
    # with actual, alert signatures (from the security software)
    # Output: {
    #   "type": str,
    #   "data": any,
    #   "score": (optional) int
    # }
    def make_struct_for_matching(self, data):
        struct = {
            "type": self.match_policy.match_type.value,
            "data": data,
        }

        if self.match_policy.match_score is not None:
            struct["score"] = self.match_policy.match_score

        return struct
