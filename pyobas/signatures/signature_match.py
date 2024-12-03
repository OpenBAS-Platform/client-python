from pyobas.signatures.types import MatchTypes
from pyobas.exceptions import OpenBASError

class SignatureMatch:
    def __init__(self, match_type: str, match_score: int):
        if not match_score and match_type != MatchTypes.MATCH_TYPE_SIMPLE:
            raise OpenBASError(f"Match type {match_type} requires score to be set, found score = {match_score}")
        self.match_type = match_type
        self.match_score = match_score