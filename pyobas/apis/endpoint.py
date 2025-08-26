from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject
from pyobas.utils import RequiredOptional


class Endpoint(RESTObject):
    _id_attr = "asset_id"


class EndpointManager(RESTManager):
    _path = "/endpoints"
    _obj_cls = Endpoint
    _create_attrs = RequiredOptional(
        required=(
            "endpoint_hostname",
            "endpoint_ips",
            "endpoint_platform",
            "endpoint_arch",
        ),
        optional=(
            "endpoint_mac_addresses",
            "asset_external_reference",
        ),
    )

    @exc.on_http_error(exc.OpenBASUpdateError)
    def get(self, asset_id: str, **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/" + asset_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(self, endpoint: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/agentless/upsert"
        result = self.openbas.http_post(path, post_data=endpoint, **kwargs)
        return result
