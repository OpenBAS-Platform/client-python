import unittest

from pyobas.signatures.signature_type import SignatureType
from pyobas.signatures.types import MatchTypes


class TestSignatureType(unittest.TestCase):
    fuzzy_signature_type_label = "Test signature type fuzzy"
    fuzzy_signature_type_score = 50
    fuzzy_signature_type = SignatureType(
        label=fuzzy_signature_type_label,
        match_type=MatchTypes.MATCH_TYPE_FUZZY,
        match_score=fuzzy_signature_type_score,
    )

    simple_signature_type_label = "Test signature type simple"
    simple_signature_type = SignatureType(
        label=simple_signature_type_label, match_type=MatchTypes.MATCH_TYPE_SIMPLE
    )

    def test_make_struct_create_expected_struct_for_simple_sig_type(self):
        data = "just a simple string"
        simple_struct = (
            TestSignatureType.simple_signature_type.make_struct_for_matching(data=data)
        )

        self.assertEqual(simple_struct.get("type"), MatchTypes.MATCH_TYPE_SIMPLE)
        self.assertEqual(simple_struct.get("data"), data)
        self.assertFalse("score" in simple_struct.keys())

    def test_make_struct_create_expected_struct_for_fuzzy_sig_type(self):
        data = "just another simple string"
        simple_struct = TestSignatureType.fuzzy_signature_type.make_struct_for_matching(
            data=data
        )

        self.assertEqual(simple_struct.get("type"), MatchTypes.MATCH_TYPE_FUZZY)
        self.assertEqual(simple_struct.get("data"), data)
        self.assertEqual(
            simple_struct.get("score"), TestSignatureType.fuzzy_signature_type_score
        )


if __name__ == "__main__":
    unittest.main()
