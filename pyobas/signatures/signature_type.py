from pyobas.signatures.signature_match import SignatureMatch
from pyobas.signatures.types import MatchTypes, SignatureTypes


class SignatureType:
    """Describes a signature of some time and a matching policy

    :param label: Type specifier
    :type label: SignatureTypes
    :param match_type: the matching policy to use when trying
    to match this signature type, e.g. fuzzy, simple...
    :type match_type: MatchTypes
    :param match_score: if the matching type is fuzzy, this is
    the score to use as threshold, defaults to None
    :type match_score: int, optional
    """

    def __init__(
        self,
        label: SignatureTypes,
        match_type: MatchTypes = MatchTypes.MATCH_TYPE_SIMPLE,
        match_score: int = None,
    ):
        self.label = label
        self.match_policy = SignatureMatch(match_type, match_score)

    def make_struct_for_matching(self, data):
        """Provided some `data`, formats a dictionary specifying the matching
        policy to use by the helper to match expected signatures (from expectations)
        with actual, alert signatures (from the security software)

        :param data: arbitrary data, but most often string or a number primitive
        :type: Any

        :return: dictionary of matching specifiers::
            {
              "type": str,
              "data": any,
              "score": (optional) int
            }
        :rtype: dict
        """
        struct = {
            "type": self.match_policy.match_type.value,
            "data": data,
        }

        if self.match_policy.match_score is not None:
            struct["score"] = self.match_policy.match_score

        return struct
