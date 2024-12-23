import unittest
import unittest.mock

from pyobas.configuration import Configuration
from pyobas.daemons import BaseDaemon
from pyobas.exceptions import OpenBASError

TEST_DAEMON_CONFIG_HINTS = {
    "openbas_url": {"data": "http://example.com"},
    "openbas_token": {"data": "test"},
    "log_level": {"data": "info"},
    "name": {"data": "my test daemon"},
}

TEST_DAEMON_CONFIGURATION = Configuration(config_hints=TEST_DAEMON_CONFIG_HINTS)


class DaemonForTest(BaseDaemon):
    def _setup(self):
        pass

    def _start_loop(self):
        pass


def create_mock_daemon(callback: callable = None):
    mock_setup = unittest.mock.MagicMock()
    mock_start_loop = unittest.mock.MagicMock()
    inner_mock_func = unittest.mock.MagicMock()

    class MockDaemon(BaseDaemon):
        def _setup(self):
            mock_setup()

        def _start_loop(self):
            mock_start_loop()

        def bound_method(self):
            inner_mock_func()

    return (
        MockDaemon(
            configuration=TEST_DAEMON_CONFIGURATION,
            callback=callback,
            # silence logging in tests
            logger=unittest.mock.MagicMock(),
        ),
        mock_setup,
        mock_start_loop,
        inner_mock_func,
    )


class TestBaseDaemon(unittest.TestCase):
    def test_when_no_callback_when_complete_config_ctor_ok(self):
        daemon = DaemonForTest(configuration=TEST_DAEMON_CONFIGURATION)

        self.assertIsInstance(daemon, BaseDaemon)

    def test_when_no_callback_when_lacking_config_key_ctor_throws(self):
        with self.assertRaises(Exception):
            DaemonForTest(configuration=Configuration(config_hints={}))

    def test_when_no_callback_daemon_cant_start(self):
        daemon, mock_setup, mock_start_loop, _ = create_mock_daemon()

        with self.assertRaises(OpenBASError):
            daemon.start()

        mock_setup.assert_not_called()
        mock_start_loop.assert_not_called()

    def test_when_callback_daemon_can_start(self):
        daemon, mock_setup, mock_start_loop, _ = create_mock_daemon(lambda: None)

        daemon.start()

        mock_setup.assert_called_once()
        mock_start_loop.assert_called_once()

    def test_when_callback_is_bound_method_daemon_can_call(self):
        daemon, mock_setup, mock_start_loop, inner_mock_func = create_mock_daemon()
        daemon.set_callback(daemon.bound_method)

        daemon._try_callback()

        inner_mock_func.assert_called_once()

    def test_when_callback_is_func_with_collector_parameter_daemon_can_call(self):
        daemon, mock_setup, mock_start_loop, _ = create_mock_daemon()
        inner_mock_func = unittest.mock.MagicMock()
        daemon.set_callback(lambda collector: inner_mock_func())

        daemon._try_callback()

        inner_mock_func.assert_called_once()

    def test_when_callback_is_func_with_other_parameter_daemon_cant_call(self):
        daemon, mock_setup, mock_start_loop, _ = create_mock_daemon()
        inner_mock_func = unittest.mock.MagicMock()
        daemon.set_callback(lambda other_parameter: inner_mock_func())

        daemon._try_callback()

        inner_mock_func.assert_not_called()


if __name__ == "__main__":
    unittest.main()
