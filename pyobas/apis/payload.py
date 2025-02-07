from typing import Any, Dict, List

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

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert_bulk(
        self, payloads: List[Dict[str, Any]], **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/upsert/bulk"
        result = self.openbas.http_post(
            path, post_data={"payloads": payloads}, **kwargs
        )
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def deprecate(
        self, payloads_processed: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/deprecate"
        result = self.openbas.http_post(path, post_data=payloads_processed, **kwargs)
        return result
