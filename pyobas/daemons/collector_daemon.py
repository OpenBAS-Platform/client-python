import sched
import time

from pyobas.daemons import BaseDaemon
from pyobas.utils import PingAlive

DEFAULT_PERIOD_SECONDS = 60


class CollectorDaemon(BaseDaemon):
    """Implementation of a daemon of Collector type. Note that it requires
    specific configuration keys to run its setup.
    `collector_icon_filepath`: relative path to an icon image (preferably PNG)
    `collector_id`: unique identifier for the collector (UUIDv4)
    `collector_period`: time to wait in seconds between each loop execution; note
    that this time is added to the time the loop takes to run, so the actual total
    time between each loop start is time_of_loop+period.
    """

    def _setup(self):
        if self._configuration.get("collector_period") is None:
            self._configuration.set("collector_period", DEFAULT_PERIOD_SECONDS)
        icon_path = self._configuration.get("collector_icon_filepath")
        icon_name = self._configuration.get("collector_id") + ".png"
        with open(icon_path, "rb") as icon_file_handle:
            collector_icon = (icon_name, icon_file_handle, "image/png")
            document = self.api.document.upsert(document={}, file=collector_icon)
            if self._configuration.get("collector_platform") is not None:
                security_platform = self.api.security_platform.upsert(
                    {
                        "asset_name": self._configuration.get("collector_name"),
                        "asset_external_reference": self._configuration.get(
                            "collector_id"
                        ),
                        "security_platform_type": self._configuration.get(
                            "collector_platform"
                        ),
                        "security_platform_logo_light": document.get("document_id"),
                        "security_platform_logo_dark": document.get("document_id"),
                    }
                )
            else:
                security_platform = {}
            security_platform_id = security_platform.get("asset_id")
            config = {
                "collector_id": self._configuration.get("collector_id"),
                "collector_name": self._configuration.get("collector_name"),
                "collector_type": self._configuration.get("collector_type"),
                "collector_period": self._configuration.get("collector_period"),
                "collector_security_platform": security_platform_id,
            }
        with open(icon_path, "rb") as icon_file_handle:
            collector_icon = (icon_name, icon_file_handle, "image/png")
            self.api.collector.create(config, collector_icon)

        PingAlive(self.api, config, self.logger, "collector").start()

    def _start_loop(self):
        scheduler = sched.scheduler(time.time, time.sleep)
        delay = self._configuration.get("collector_period")
        self._try_callback()
        scheduler.enter(
            delay=delay,
            priority=1,
            action=self.__schedule,
            argument=(scheduler, self._try_callback, delay),
        )
        scheduler.run()

    def __schedule(self, scheduler, callback, delay):
        callback()
        scheduler.enter(
            delay=delay,
            priority=1,
            action=self.__schedule,
            argument=(scheduler, callback, delay),
        )
