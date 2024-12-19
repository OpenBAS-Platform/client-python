import unittest.mock
from uuid import uuid4

from pyobas.apis import InjectExpectationManager, PreventionExpectation

from pyobas.apis.inject_expectation.model import DetectionExpectation


class TestExpectation(unittest.TestCase):
    @unittest.mock.patch("pyobas.apis.InjectExpectationManager.update")
    def test_when_detection_model_when_success_update_labels_correct(self, mock_update):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        model = DetectionExpectation(**{
            "inject_expectation_id": inject_expectation_id,
            "inject_expectation_signatures": []
        }, api_client=InjectExpectationManager(None)) # we don't care to construct a functional object

        model.update(success=True, sender_id=sender_id, metadata={})

        mock_update.assert_called_once_with(inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Detected",
                "is_success": True,
                "metadata": {},
            })

    @unittest.mock.patch("pyobas.apis.InjectExpectationManager.update")
    def test_when_detection_model_when_failure_update_labels_correct(self, mock_update):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        model = DetectionExpectation(**{
            "inject_expectation_id": inject_expectation_id,
            "inject_expectation_signatures": []
        }, api_client=InjectExpectationManager(None)) # we don't care to construct a functional object

        model.update(success=False, sender_id=sender_id, metadata={})

        mock_update.assert_called_once_with(inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Not Detected",
                "is_success": False,
                "metadata": {},
            })

    @unittest.mock.patch("pyobas.apis.InjectExpectationManager.update")
    def test_when_prevention_model_when_success_update_labels_correct(self, mock_update):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        model = PreventionExpectation(**{
            "inject_expectation_id": inject_expectation_id,
            "inject_expectation_signatures": []
        }, api_client=InjectExpectationManager(None)) # we don't care to construct a functional object

        model.update(success=True, sender_id=sender_id, metadata={})

        mock_update.assert_called_once_with(inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Prevented",
                "is_success": True,
                "metadata": {},
            })

    @unittest.mock.patch("pyobas.apis.InjectExpectationManager.update")
    def test_when_prevention_model_when_failure_update_labels_correct(self, mock_update):
        inject_expectation_id = uuid4()
        sender_id = uuid4()
        model = PreventionExpectation(**{
            "inject_expectation_id": inject_expectation_id,
            "inject_expectation_signatures": []
        }, api_client=InjectExpectationManager(None)) # we don't care to construct a functional object

        model.update(success=False, sender_id=sender_id, metadata={})

        mock_update.assert_called_once_with(inject_expectation_id,
            inject_expectation={
                "collector_id": sender_id,
                "result": "Not Prevented",
                "is_success": False,
                "metadata": {},
            })

if __name__ == '__main__':
    unittest.main()
