import json
import os
import ssl
import tempfile
import threading
import time
import traceback
from typing import Callable, Dict, List, Optional, Union

import pika

from pybas import OpenBAS

TRUTHY: List[str] = ["yes", "true", "True"]
FALSY: List[str] = ["no", "false", "False"]


# As cert must be written in files to be loaded in ssl context
# Creates a temporary file in the most secure manner possible
def data_to_temp_file(data):
    # The file is readable and writable only by the creating user ID.
    # If the operating system uses permission bits to indicate whether a
    # file is executable, the file is executable by no one. The file
    # descriptor is not inherited by children of this process.
    file_descriptor, file_path = tempfile.mkstemp()
    with os.fdopen(file_descriptor, "w") as open_file:
        open_file.write(data)
        open_file.close()
    return file_path


def is_memory_certificate(certificate):
    return certificate.startswith("-----BEGIN")


def ssl_cert_chain(ssl_context, cert_data, key_data, passphrase):
    if cert_data is None:
        return

    cert_file_path = None
    key_file_path = None

    # Cert loading
    if cert_data is not None and is_memory_certificate(cert_data):
        cert_file_path = data_to_temp_file(cert_data)
    cert = cert_file_path if cert_file_path is not None else cert_data

    # Key loading
    if key_data is not None and is_memory_certificate(key_data):
        key_file_path = data_to_temp_file(key_data)
    key = key_file_path if key_file_path is not None else key_data

    # Load cert
    ssl_context.load_cert_chain(cert, key, passphrase)
    # Remove temp files
    if cert_file_path is not None:
        os.unlink(cert_file_path)
    if key_file_path is not None:
        os.unlink(key_file_path)


def ssl_verify_locations(ssl_context, certdata):
    if certdata is None:
        return

    if is_memory_certificate(certdata):
        ssl_context.load_verify_locations(cadata=certdata)
    else:
        ssl_context.load_verify_locations(cafile=certdata)


def get_config_variable(
    env_var: str,
    yaml_path: List,
    config: Dict = {},
    isNumber: Optional[bool] = False,
    default=None,
    required=False,
) -> Union[bool, int, None, str]:
    """[summary]

    :param env_var: environment variable name
    :param yaml_path: path to yaml config
    :param config: client config dict, defaults to {}
    :param isNumber: specify if the variable is a number, defaults to False
    :param default: default value
    """

    if os.getenv(env_var) is not None:
        result = os.getenv(env_var)
    elif yaml_path is not None:
        if yaml_path[0] in config and yaml_path[1] in config[yaml_path[0]]:
            result = config[yaml_path[0]][yaml_path[1]]
        else:
            return default
    else:
        return default

    if result in TRUTHY:
        return True
    if result in FALSY:
        return False
    if isNumber:
        return int(result)

    if (
        required
        and default is None
        and (result is None or (isinstance(result, str) and len(result) == 0))
    ):
        raise ValueError("The configuration " + env_var + " is required")

    if isinstance(result, str) and len(result) == 0:
        return default

    return result


def create_mq_ssl_context(config) -> ssl.SSLContext:
    use_ssl_ca = get_config_variable("MQ_USE_SSL_CA", ["mq", "use_ssl_ca"], config)
    use_ssl_cert = get_config_variable(
        "MQ_USE_SSL_CERT", ["mq", "use_ssl_cert"], config
    )
    use_ssl_key = get_config_variable("MQ_USE_SSL_KEY", ["mq", "use_ssl_key"], config)
    use_ssl_reject_unauthorized = get_config_variable(
        "MQ_USE_SSL_REJECT_UNAUTHORIZED",
        ["mq", "use_ssl_reject_unauthorized"],
        config,
        False,
        False,
    )
    use_ssl_passphrase = get_config_variable(
        "MQ_USE_SSL_PASSPHRASE", ["mq", "use_ssl_passphrase"], config
    )
    ssl_context = ssl.create_default_context()
    # If no rejection allowed, use private function to generate unverified context
    if not use_ssl_reject_unauthorized:
        # noinspection PyUnresolvedReferences,PyProtectedMember
        ssl_context = ssl._create_unverified_context()
    ssl_verify_locations(ssl_context, use_ssl_ca)
    # Thanks to https://bugs.python.org/issue16487 is not possible today to easily use memory pem
    # in SSL context. We need to write it to a temporary file before
    ssl_cert_chain(ssl_context, use_ssl_cert, use_ssl_key, use_ssl_passphrase)
    return ssl_context


class ListenQueue(threading.Thread):
    def __init__(
        self,
        helper,
        config: Dict,
        injector_config: Dict,
        callback,
    ) -> None:
        threading.Thread.__init__(self)
        self.pika_credentials = None
        self.pika_parameters = None
        self.pika_connection = None
        self.channel = None

        self.callback = callback
        self.config = config
        self.host = injector_config["connection"]["host"]
        self.vhost = injector_config["connection"]["vhost"]
        self.use_ssl = injector_config["connection"]["use_ssl"]
        self.port = injector_config["connection"]["port"]
        self.user = injector_config["connection"]["user"]
        self.password = injector_config["connection"]["pass"]
        self.queue_name = injector_config["listen"]
        self.exit_event = threading.Event()
        self.thread = None

    # noinspection PyUnusedLocal
    def _process_message(self, channel, method, properties, body) -> None:
        """process a message from the rabbit queue

        :param channel: channel instance
        :type channel: callable
        :param method: message methods
        :type method: callable
        :param properties: unused
        :type properties: str
        :param body: message body (data)
        :type body: str or bytes or bytearray
        """
        json_data = json.loads(body)
        # Message should be ack before processing as we don't own the processing
        # Not ACK the message here may lead to infinite re-deliver if the connector is broken
        # Also ACK, will not have any impact on the blocking aspect of the following functions
        channel.basic_ack(delivery_tag=method.delivery_tag)
        self.thread = threading.Thread(target=self._data_handler, args=[json_data])
        self.thread.start()

    def _data_handler(self, json_data) -> None:
        self.callback(json_data)

    def run(self) -> None:
        print("Starting ListenQueue thread")
        while not self.exit_event.is_set():
            try:
                print("ListenQueue connecting to rabbitMq.")
                # Connect the broker
                self.pika_credentials = pika.PlainCredentials(self.user, self.password)
                self.pika_parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    virtual_host=self.vhost,
                    credentials=self.pika_credentials,
                    ssl_options=(
                        pika.SSLOptions(create_mq_ssl_context(self.config), self.host)
                        if self.use_ssl
                        else None
                    ),
                )
                self.pika_connection = pika.BlockingConnection(self.pika_parameters)
                self.channel = self.pika_connection.channel()
                try:
                    # confirm_delivery is only for cluster mode rabbitMQ
                    # when not in cluster mode this line raise an exception
                    self.channel.confirm_delivery()
                except Exception as err:  # pylint: disable=broad-except
                    print(str(err))
                self.channel.basic_qos(prefetch_count=1)
                assert self.channel is not None
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except Exception as err:  # pylint: disable=broad-except
                try:
                    self.pika_connection.close()
                except Exception as errInException:
                    print(str(errInException))
                traceback.print_exc()
                # Wait some time and then retry ListenQueue again.
                time.sleep(10)

    def stop(self):
        print("Preparing ListenQueue for clean shutdown")
        self.exit_event.set()
        self.pika_connection.close()
        if self.thread:
            self.thread.join()


class PingAlive(threading.Thread):
    def __init__(self, api, config) -> None:
        threading.Thread.__init__(self)
        self.api = api
        self.config = config
        self.in_error = False
        self.exit_event = threading.Event()

    def ping(self) -> None:
        while not self.exit_event.is_set():
            try:
                print("PingAlive running.")
                self.api.injector.create(self.config)
            except Exception as e:  # pylint: disable=broad-except
                print(str(e))
            self.exit_event.wait(40)

    def run(self) -> None:
        print("Starting PingAlive thread")
        self.ping()

    def stop(self) -> None:
        print("Preparing PingAlive for clean shutdown")
        self.exit_event.set()


class OpenBASInjectorHelper:
    def __init__(self, api: OpenBAS, config: Dict, injector_config: Dict) -> None:
        self.api = api
        self.config = config
        self.injector_config = injector_config
        self.connect_run_and_terminate = False
        # Start ping thread
        if not self.connect_run_and_terminate:
            self.ping = PingAlive(
                self.api,
                self.config,
            )
            self.ping.start()
        self.listen_queue = None

    def listen(self, message_callback: Callable[[Dict], str]) -> None:
        self.listen_queue = ListenQueue(
            self,
            self.config,
            self.injector_config,
            message_callback,
        )
        self.listen_queue.start()
