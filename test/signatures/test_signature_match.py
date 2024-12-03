import unittest

from pyobas.exceptions import OpenBASError
from pyobas.signatures.signature_match import SignatureMatch
from pyobas.signatures.types import MatchTypes


class TestSignatureMatch(unittest.TestCase):
    def test_non_simple_match_with_non_null_score_throws(self):
        score = None
        self.assertRaises(
            OpenBASError, SignatureMatch, MatchTypes.MATCH_TYPE_FUZZY, score
        )

    def test_simple_match_with_null_score_does_not_throw(self):
        score = None
        SignatureMatch(match_type=MatchTypes.MATCH_TYPE_SIMPLE, match_score=score)

    def test_fuzzy_match_with_0_score_does_not_throw(self):
        score = 0
        SignatureMatch(match_type=MatchTypes.MATCH_TYPE_FUZZY, match_score=score)


if __name__ == "__main__":
    unittest.main()
