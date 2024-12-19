import sched
import time

from pyobas.daemons import BaseDaemon
from pyobas.utils import PingAlive


class CollectorDaemon(BaseDaemon):
    def _setup(self):
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
