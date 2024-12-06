import unittest

from pyobas.signatures.signature_type import SignatureType
from pyobas.signatures.types import MatchTypes, SignatureTypes


class TestSignatureType(unittest.TestCase):
    def test_make_struct_create_expected_struct_for_simple_sig_type(self):
        simple_signature_type_label = SignatureTypes.SIG_TYPE_HOSTNAME
        simple_signature_type = SignatureType(
            label=simple_signature_type_label, match_type=MatchTypes.MATCH_TYPE_SIMPLE
        )

        data = "just a simple string"
        simple_struct = simple_signature_type.make_struct_for_matching(data=data)

        self.assertEqual(simple_struct.get("type"), MatchTypes.MATCH_TYPE_SIMPLE.value)
        self.assertEqual(simple_struct.get("data"), data)
        self.assertFalse("score" in simple_struct.keys())

    def test_make_struct_create_expected_struct_for_fuzzy_sig_type(self):
        fuzzy_signature_type_label = SignatureTypes.SIG_TYPE_HOSTNAME
        fuzzy_signature_type_score = 50
        fuzzy_signature_type = SignatureType(
            label=fuzzy_signature_type_label,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=fuzzy_signature_type_score,
        )

        data = "just another simple string"
        simple_struct = fuzzy_signature_type.make_struct_for_matching(data=data)

        self.assertEqual(simple_struct.get("type"), MatchTypes.MATCH_TYPE_FUZZY.value)
        self.assertEqual(simple_struct.get("data"), data)
        self.assertEqual(simple_struct.get("score"), fuzzy_signature_type_score)

    def test_make_struct_create_expected_struct_for_fuzzy_sig_type_when_score_is_0(
        self,
    ):
        fuzzy_signature_type_label = SignatureTypes.SIG_TYPE_HOSTNAME
        fuzzy_signature_type_score = 0
        fuzzy_signature_type = SignatureType(
            label=fuzzy_signature_type_label,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=fuzzy_signature_type_score,
        )

        data = "just another simple string"
        simple_struct = fuzzy_signature_type.make_struct_for_matching(data=data)

        self.assertEqual(simple_struct.get("type"), MatchTypes.MATCH_TYPE_FUZZY.value)
        self.assertEqual(simple_struct.get("data"), data)
        self.assertEqual(simple_struct.get("score"), fuzzy_signature_type_score)


if __name__ == "__main__":
    unittest.main()
