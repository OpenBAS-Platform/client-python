from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Payload(RESTObject):
    _id_attr = "payload_id"


class PayloadManager(RESTManager):
    _path = "/payloads"
    _obj_cls = Payload

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(self, payload: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/upsert"
        result = self.openbas.http_post(path, post_data=payload, **kwargs)
        return result
