import unittest
from unittest.mock import MagicMock

from helpers import OpenBASDetectionHelper


class TestOpenBASDetectionHelper(unittest.TestCase):

    def setUp(self):
        self.mock_logger = MagicMock()
        self.relevant_signatures_types = [
            "parent_process_name",
            "command_line",
            "command_line_base64",
        ]
        self.detection_helper = OpenBASDetectionHelper(
            self.mock_logger, self.relevant_signatures_types
        )

    def test_should_match_alert_parent_process_name(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": ["obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9"],
                "score": 80,
            }
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_not_match_alert_parent_process_when_empty(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {}

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)

    def test_should_not_match_alert_parent_process_name(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": ["obas-implant-44942182-fb2f-41e3-a3c9-cb0eac1cd2d9"],
                "score": 80,
            }
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)

    def test_should_match_alert_parent_process_name_from_list(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": [
                    "not_matching_process_name",
                    "obas-implant-44942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
                    "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
                ],
                "score": 80,
            }
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_not_match_alert_parent_process_name_from_non_matching_list(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": ["not_matching_process_name", "not_matching_process_name"],
                "score": 80,
            }
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)

    def test_should_not_match_alert_parent_process_name_from_list_with_None(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            }
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": [None],
                "score": 80,
            }
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
