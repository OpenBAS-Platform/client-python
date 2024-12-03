from pyobas.exceptions import OpenBASError
from pyobas.signatures.types import MatchTypes


class SignatureMatch:
    def __init__(self, match_type: MatchTypes, match_score: int | None):
        if match_score is None and match_type != MatchTypes.MATCH_TYPE_SIMPLE:
            raise OpenBASError(
                f"Match type {match_type} requires score to be set, found score = {match_score}"
            )
        self.match_type = match_type
        self.match_score = match_score
