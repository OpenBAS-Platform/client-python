import json
import os
import sched
import ssl
import tempfile
import threading
import time
import traceback
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Union

import pika
import yaml
from thefuzz import fuzz

from pyobas import OpenBAS, utils

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
        config: Dict,
        injector_config: Dict,
        logger,
        callback,
    ) -> None:
        threading.Thread.__init__(self)
        self.pika_credentials = None
        self.pika_parameters = None
        self.pika_connection = None
        self.channel = None

        self.callback = callback
        self.config = config
        self.logger = logger
        self.host = injector_config.connection["host"]
        self.vhost = injector_config.connection["vhost"]
        self.use_ssl = injector_config.connection["use_ssl"]
        self.port = injector_config.connection["port"]
        self.user = injector_config.connection["user"]
        self.password = injector_config.connection["pass"]
        self.queue_name = injector_config.listen
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
        self.logger.info("Starting ListenQueue thread")
        while not self.exit_event.is_set():
            try:
                self.logger.info("ListenQueue connecting to RabbitMQ.")
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
                    self.logger.error(str(err))
                self.channel.basic_qos(prefetch_count=1)
                assert self.channel is not None
                self.channel.basic_consume(
                    queue=self.queue_name, on_message_callback=self._process_message
                )
                self.channel.start_consuming()
            except Exception:  # pylint: disable=broad-except
                try:
                    self.pika_connection.close()
                except Exception as errInException:
                    self.logger.error(str(errInException))
                traceback.print_exc()
                # Wait some time and then retry ListenQueue again.
                time.sleep(10)

    def stop(self):
        self.logger.info("Preparing ListenQueue for clean shutdown")
        self.exit_event.set()
        self.pika_connection.close()
        if self.thread:
            self.thread.join()


class PingAlive(threading.Thread):
    def __init__(self, api, config, logger, ping_type) -> None:
        threading.Thread.__init__(self)
        self.ping_type = ping_type
        self.api = api
        self.config = config
        self.logger = logger
        self.in_error = False
        self.exit_event = threading.Event()

    def ping(self) -> None:
        while not self.exit_event.is_set():
            try:
                if self.ping_type == "injector":
                    self.api.injector.create(self.config, False)
                else:
                    self.api.collector.create(self.config, False)
            except Exception as err:  # pylint: disable=broad-except
                self.logger.error("Error pinging the API: " + str(err))
            self.exit_event.wait(40)

    def run(self) -> None:
        self.logger.info("Starting PingAlive thread")
        self.ping()

    def stop(self) -> None:
        self.logger.info("Preparing PingAlive for clean shutdown")
        self.exit_event.set()


class OpenBASConfigHelper:
    def __init__(self, base_path, variables: Dict):
        config_file_path = os.path.dirname(os.path.abspath(base_path)) + "/config.yml"
        self.file_config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )
        self.variables = variables

    def get_conf(self, variable, is_number=None, default=None, required=None):
        var = self.variables.get(variable)
        if var is None:
            return default
        # If direct variable
        if var.get("data") is not None:
            return var.get("data")
        # Else if file or env variable
        return get_config_variable(
            env_var=var["env"],
            yaml_path=var["file_path"],
            config=self.file_config,
            isNumber=var["is_number"] if "is_number" in var else is_number,
            default=var["default"] if "default" in var else default,
            required=required,
        )


class OpenBASCollectorHelper:
    def __init__(
        self, config: OpenBASConfigHelper, icon, security_platform_type=None
    ) -> None:
        self.config_helper = config
        self.api = OpenBAS(
            url=config.get_conf("openbas_url"),
            token=config.get_conf("openbas_token"),
        )

        self.logger_class = utils.logger(
            config.get_conf("collector_log_level", default="info").upper(),
            config.get_conf("collector_json_logging", default=True),
        )
        self.collector_logger = self.logger_class(config.get_conf("collector_name"))

        icon_name = config.get_conf("collector_id") + ".png"

        security_platform_id = None
        if security_platform_type is not None:
            collector_icon = (icon_name, open(icon, "rb"), "image/png")
            document = self.api.document.upsert(document={}, file=collector_icon)
            security_platform = self.api.security_platform.upsert(
                {
                    "asset_name": config.get_conf("collector_name"),
                    "asset_external_reference": config.get_conf("collector_id"),
                    "security_platform_type": security_platform_type,
                    "security_platform_logo_light": document.get("document_id"),
                    "security_platform_logo_dark": document.get("document_id"),
                }
            )
            security_platform_id = security_platform.get("asset_id")

        self.config = {
            "collector_id": config.get_conf("collector_id"),
            "collector_name": config.get_conf("collector_name"),
            "collector_type": config.get_conf("collector_type"),
            "collector_period": config.get_conf("collector_period"),
            "collector_security_platform": security_platform_id,
        }

        collector_icon = (icon_name, open(icon, "rb"), "image/png")
        self.api.collector.create(self.config, collector_icon)
        self.connect_run_and_terminate = False
        # self.api.injector.create(self.config)
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # Start ping thread
        if not self.connect_run_and_terminate:
            self.ping = PingAlive(
                self.api, self.config, self.collector_logger, "collector"
            )
            self.ping.start()
        self.listen_queue = None

    def _schedule(self, scheduler, message_callback, delay):
        # Execute
        try:
            message_callback()
        except Exception as err:  # pylint: disable=broad-except
            self.collector_logger.error("Error collecting: " + str(err))

        # Then schedule the next execution
        scheduler.enter(delay, 1, self._schedule, (scheduler, message_callback, delay))

    def schedule(self, message_callback, delay):
        # Start execution directly
        try:
            message_callback()
            now = datetime.now(timezone.utc).isoformat()
            self.api.collector.update(
                self.config_helper.get_conf("collector_id"),
                {"collector_last_execution": now},
            )
        except Exception as err:  # pylint: disable=broad-except
            self.collector_logger.error("Error collecting: " + str(err))
        # Then schedule the next execution
        self.scheduler.enter(
            delay, 1, self._schedule, (self.scheduler, message_callback, delay)
        )
        self.scheduler.run()


class OpenBASInjectorHelper:
    def __init__(self, config: OpenBASConfigHelper, icon) -> None:
        self.api = OpenBAS(
            url=config.get_conf("openbas_url"),
            token=config.get_conf("openbas_token"),
        )
        # Get the mq configuration from api
        self.config = {
            "injector_id": config.get_conf("injector_id"),
            "injector_name": config.get_conf("injector_name"),
            "injector_type": config.get_conf("injector_type"),
            "injector_contracts": config.get_conf("injector_contracts"),
            "injector_custom_contracts": config.get_conf(
                "injector_custom_contracts", default=False
            ),
            "injector_category": config.get_conf("injector_category", default=None),
            "injector_executor_commands": config.get_conf(
                "injector_executor_commands", default=None
            ),
            "injector_executor_clear_commands": config.get_conf(
                "injector_executor_clear_commands", default=None
            ),
        }

        self.logger_class = utils.logger(
            config.get_conf("injector_log_level", default="info").upper(),
            config.get_conf("injector_json_logging", default=True),
        )
        self.injector_logger = self.logger_class(config.get_conf("injector_name"))

        icon_name = config.get_conf("injector_type") + ".png"
        injector_icon = (icon_name, icon, "image/png")
        self.injector_config = self.api.injector.create(self.config, injector_icon)
        self.connect_run_and_terminate = False
        self.scheduler = sched.scheduler(time.time, time.sleep)
        # Start ping thread
        if not self.connect_run_and_terminate:
            self.ping = PingAlive(
                self.api, self.config, self.injector_logger, "injector"
            )
            self.ping.start()
        self.listen_queue = None

    def listen(self, message_callback: Callable[[Dict], None]) -> None:
        self.listen_queue = ListenQueue(
            self.config, self.injector_config, self.injector_logger, message_callback
        )
        self.listen_queue.start()


class OpenBASDetectionHelper:
    def __init__(self, logger, relevant_signatures_types) -> None:
        self.logger = logger
        self.relevant_signatures_types = relevant_signatures_types

    def match_alert_element_fuzzy(self, signature_value, alert_values, fuzzy_scoring):
        for alert_value in alert_values:
            self.logger.info(
                "Comparing alert value (" + alert_value + ", " + signature_value + ")"
            )
            ratio = fuzz.ratio(alert_value, signature_value)
            if ratio > fuzzy_scoring:
                self.logger.info("MATCHING! (score: " + str(ratio) + ")")
                return True
        return False

    def match_alert_elements(self, signatures, alert_data):
        # Example for alert_data
        # {"process_name": {"list": ["xx", "yy"], "fuzzy": 90}}
        relevant_signatures = [
            s for s in signatures if s["type"] in self.relevant_signatures_types
        ]

        # Matching logics
        signatures_number = len(relevant_signatures)
        matching_number = 0
        for signature in relevant_signatures:
            alert_data_for_signature = alert_data[signature["type"]]
            signature_result = False
            if alert_data_for_signature["type"] == "fuzzy":
                signature_result = self.match_alert_element_fuzzy(
                    signature["value"],
                    alert_data_for_signature["data"],
                    alert_data_for_signature["score"],
                )
            elif alert_data_for_signature["type"] == "simple":
                signature_result = signature["value"] in str(
                    alert_data_for_signature["data"]
                )

            if signature_result:
                matching_number = matching_number + 1

        if signatures_number == matching_number:
            return True
        return False
