from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Inject(RESTObject):
    _id_attr = None


class InjectManager(RESTManager):
    _path = "/injects"
    _obj_cls = Inject

    @exc.on_http_error(exc.OpenBASUpdateError)
    def execution_callback(
        self, inject_id: str, data: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/execution/callback/{inject_id}"
        result = self.openbas.http_post(path, post_data=data, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def execution_reception(
        self, inject_id: str, data: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/execution/reception/{inject_id}"
        result = self.openbas.http_post(path, post_data=data, **kwargs)
        return result
