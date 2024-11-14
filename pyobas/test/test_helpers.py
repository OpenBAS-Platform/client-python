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

    def test_should_match_alert_parent_process_name_and_clear_command_line(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            },
            {
                "type": "command_line",
                "value": "SCHTASKS /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10\n",
            },
            {
                "type": "command_line_base64",
                "value": "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK",
            },
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": ["obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9"],
                "score": 80,
            },
            "command_line": {
                "type": "fuzzy",
                "data": [
                    '"schtasks.exe" /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10'
                ],
                "score": 60,
            },
            "command_line_base64": {
                "type": "fuzzy",
                "data": [
                    '"schtasks.exe" /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10'
                ],
                "score": 60,
            },
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_not_match_alert_parent_process_name(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            },
            {
                "type": "command_line",
                "value": "SCHTASKS /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10\n",
            },
            {
                "type": "command_line_base64",
                "value": "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK",
            },
        ]
        alert_data = {
            "parent_process_name": {
                "type": "fuzzy",
                "data": ["obas-implant-44942182-fb2f-41e3-a3c9-cb0eac1cd2d9"],
                "score": 80,
            },
            "command_line": {
                "type": "fuzzy",
                "data": ['"schtasks.exe"'],
                "score": 60,
            },
            "command_line_base64": {
                "type": "fuzzy",
                "data": ['"schtasks.exe"'],
                "score": 60,
            },
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)

    def test_should_match_alert_with_clear_alert_command_line(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            },
            {
                "type": "command_line",
                "value": "SCHTASKS /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10\n",
            },
            {
                "type": "command_line_base64",
                "value": "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK",
            },
        ]
        alert_data = {
            "parent_process_name": {"type": "fuzzy", "data": ["pwsh.exe"], "score": 80},
            "command_line": {
                "type": "fuzzy",
                "data": [
                    '"schtasks.exe" /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10'
                ],
                "score": 60,
            },
            "command_line_base64": {
                "type": "fuzzy",
                "data": [
                    '"schtasks.exe" /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10'
                ],
                "score": 60,
            },
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_match_alert_with_base64_alert_command_line(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-04942182-fb2f-41e3-a3c9-cb0eac1cd2d9",
            },
            {
                "type": "command_line",
                "value": "SCHTASKS /Create /SC ONCE /TN spawn /TR C:\\windows\\system32\\cmd.exe /ST 20:10\n",
            },
            {
                "type": "command_line_base64",
                "value": "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK",
            },
        ]
        alert_data = {
            "parent_process_name": {"type": "fuzzy", "data": ["pwsh.exe"], "score": 80},
            "command_line": {
                "type": "fuzzy",
                "data": [
                    "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK"
                ],
                "score": 60,
            },
            "command_line_base64": {
                "type": "fuzzy",
                "data": [
                    "U0NIVEFTS1MgL0NyZWF0ZSAvU0MgT05DRSAvVE4gc3Bhd24gL1RSIEM6XHdpbmRvd3Ncc3lzdGVtMzJcY21kLmV4ZSAvU1QgMjA6MTAK"
                ],
                "score": 60,
            },
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_match_alert_with_command_line_detected_as_file_on_alert(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-82dc95ac-2d98-41a5-8a74-4103286e0342",
            },
            {
                "type": "command_line",
                "value": "curl -o /tmp/eicar.com.txt https://secure.eicar.org/eicar.com.txt",
            },
            {
                "type": "command_line_base64",
                "value": "Y3VybCAtbyAvdG1wL2VpY2FyLmNvbS50eHQgaHR0cHM6Ly9zZWN1cmUuZWljYXIub3JnL2VpY2FyLmNvbS50eHQ=",
            },
        ]
        alert_data = {
            "parent_process_name": {"type": "fuzzy", "data": [], "score": 80},
            "file_name": {"type": "fuzzy", "data": ["eicar.com.txt"], "score": 60},
            "process_name": {"type": "fuzzy", "data": ["eicar.com.txt"], "score": 60},
            "command_line": {"type": "fuzzy", "data": [], "score": 60},
            "command_line_base64": {"type": "fuzzy", "data": [], "score": 60},
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertTrue(result)

    def test_should_not_match_alert_with_command_line_detected_as_file_on_alert(self):
        signatures = [
            {
                "type": "parent_process_name",
                "value": "obas-implant-82dc95ac-2d98-41a5-8a74-4103286e0342",
            },
            {
                "type": "command_line",
                "value": "curl -o /tmp/eicar.com.txt https://secure.eicar.org/eicar.com.txt",
            },
            {
                "type": "command_line_base64",
                "value": "Y3VybCAtbyAvdG1wL2VpY2FyLmNvbS50eHQgaHR0cHM6Ly9zZWN1cmUuZWljYXIub3JnL2VpY2FyLmNvbS50eHQ=",
            },
        ]
        alert_data = {
            "parent_process_name": {"type": "fuzzy", "data": [], "score": 80},
            "file_name": {"type": "fuzzy", "data": ["eicar.zip"], "score": 60},
            "process_name": {"type": "fuzzy", "data": ["eicar.zip"], "score": 60},
            "command_line": {"type": "fuzzy", "data": [], "score": 60},
            "command_line_base64": {"type": "fuzzy", "data": [], "score": 60},
        }

        result = self.detection_helper.match_alert_elements(signatures, alert_data)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
