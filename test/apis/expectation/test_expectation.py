import unittest.mock
from uuid import uuid4

from pyobas.apis.inject_expectation.model import (
    DetectionExpectation,
    PreventionExpectation,
)
from pyobas.signatures.signature_type import SignatureType
from pyobas.signatures.types import MatchTypes, SignatureTypes


def create_mock_api_client():
    return unittest.mock.MagicMock()


class TestExpectation(unittest.TestCase):
    def test_when_detection_model_when_success_update_labels_correct(self):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        api_client = create_mock_api_client()
        model = DetectionExpectation(
            **{
                "inject_expectation_id": inject_expectation_id,
                "inject_expectation_signatures": [],
            },
            api_client=api_client,
        )

        model.update(success=True, sender_id=sender_id, metadata={})

        api_client.update.assert_called_once_with(
            inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Detected",
                "is_success": True,
                "metadata": {},
            },
        )

    def test_when_detection_model_when_failure_update_labels_correct(self):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        api_client = create_mock_api_client()
        model = DetectionExpectation(
            **{
                "inject_expectation_id": inject_expectation_id,
                "inject_expectation_signatures": [],
            },
            api_client=api_client,
        )  # we don't care to construct a functional object

        model.update(success=False, sender_id=sender_id, metadata={})

        api_client.update.assert_called_once_with(
            inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Not Detected",
                "is_success": False,
                "metadata": {},
            },
        )

    def test_when_prevention_model_when_success_update_labels_correct(self):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        api_client = create_mock_api_client()
        model = PreventionExpectation(
            **{
                "inject_expectation_id": inject_expectation_id,
                "inject_expectation_signatures": [],
            },
            api_client=api_client,
        )  # we don't care to construct a functional object

        model.update(success=True, sender_id=sender_id, metadata={})

        api_client.update.assert_called_once_with(
            inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Prevented",
                "is_success": True,
                "metadata": {},
            },
        )

    def test_when_prevention_model_when_failure_update_labels_correct(self):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        api_client = create_mock_api_client()
        model = PreventionExpectation(
            **{
                "inject_expectation_id": inject_expectation_id,
                "inject_expectation_signatures": [],
            },
            api_client=api_client,
        )  # we don't care to construct a functional object

        model.update(success=False, sender_id=sender_id, metadata={})

        api_client.update.assert_called_once_with(
            inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Not Prevented",
                "is_success": False,
                "metadata": {},
            },
        )

    def test_when_no_expectation_signature_is_relevant_match_alert_return_false(self):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                ],
            },
            api_client=create_mock_api_client(),
        )

        relevant_signature_types = [
            SignatureType(
                label=SignatureTypes.SIG_TYPE_HOSTNAME,
                match_type=MatchTypes.MATCH_TYPE_SIMPLE,
            )
        ]

        alert_data = (
            {  # irrelevant but aligned with expectation sigs to validate no match
                SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME.value: {
                    "type": MatchTypes.MATCH_TYPE_FUZZY.value,
                    "data": "parent.exe",
                    "score": 95,
                },
            }
        )

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertFalse(matched)

    def test_when_relevant_signature_when_none_match_alert_return_false(self):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                ],
            },
            api_client=create_mock_api_client(),
        )

        parent_process_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        relevant_signature_types = [parent_process_signature_type]

        alert_data = {
            parent_process_signature_type.label.value: parent_process_signature_type.make_struct_for_matching(
                data="not_parent.exe"
            )
        }

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertFalse(matched)

    def test_when_relevant_signature_when_all_signatures_match_alert_return_true(self):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                ],
            },
            api_client=create_mock_api_client(),
        )

        parent_process_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        relevant_signature_types = [parent_process_signature_type]

        alert_data = {
            parent_process_signature_type.label.value: parent_process_signature_type.make_struct_for_matching(
                data="parent.exe"
            )
        }

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertTrue(matched)

    def test_when_relevant_signature_when_all_signatures_match_alert_when_passing_array_return_true(
        self,
    ):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                ],
            },
            api_client=create_mock_api_client(),
        )

        parent_process_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        relevant_signature_types = [parent_process_signature_type]

        alert_data = {
            parent_process_signature_type.label.value: parent_process_signature_type.make_struct_for_matching(
                data=["parent.exe", "some_other_process"]
            )
        }

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertTrue(matched)

    def test_when_relevant_signatures_when_alert_data_missing_for_some_relevant_signatures_return_false(
        self,
    ):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                    {"type": SignatureTypes.SIG_TYPE_FILE_NAME, "value": "filename"},
                ],
            },
            api_client=create_mock_api_client(),
        )

        parent_process_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        file_name_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_FILE_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        relevant_signature_types = [
            parent_process_signature_type,
            file_name_signature_type,
        ]

        alert_data = {
            parent_process_signature_type.label.value: parent_process_signature_type.make_struct_for_matching(
                data="parent.exe"
            )
        }

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertFalse(matched)

    def test_when_relevant_signatures_when_some_alert_data_dont_match_return_false(
        self,
    ):
        model = DetectionExpectation(
            **{
                "inject_expectation_id": uuid4(),
                "inject_expectation_signatures": [
                    {
                        "type": SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
                        "value": "parent.exe",
                    },
                    {
                        "type": SignatureTypes.SIG_TYPE_FILE_NAME,
                        "value": "some_file.odt",
                    },
                ],
            },
            api_client=create_mock_api_client(),
        )

        parent_process_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_PARENT_PROCESS_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        file_name_signature_type = SignatureType(
            label=SignatureTypes.SIG_TYPE_FILE_NAME,
            match_type=MatchTypes.MATCH_TYPE_FUZZY,
            match_score=95,
        )
        relevant_signature_types = [
            parent_process_signature_type,
            file_name_signature_type,
        ]

        alert_data = {
            parent_process_signature_type.label.value: parent_process_signature_type.make_struct_for_matching(
                data="parent.exe"
            ),
            file_name_signature_type.label.value: file_name_signature_type.make_struct_for_matching(
                data="some_other_file.doc"
            ),
        }

        matched = model.match_alert(relevant_signature_types, alert_data)

        self.assertFalse(matched)


if __name__ == "__main__":
    unittest.main()
