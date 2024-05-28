from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Endpoint(RESTObject):
    _id_attr = "asset_id"


class EndpointManager(RESTManager):
    _path = "/endpoints"
    _obj_cls = Endpoint

    @exc.on_http_error(exc.OpenBASUpdateError)
    def get(self, asset_id: str, **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/" + asset_id
        result = self.openbas.http_get(path, **kwargs)
        return result
