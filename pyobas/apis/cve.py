from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Cve(RESTObject):
    _id_attr = "cve_id"


class CveManager(RESTManager):
    _path = "/cves"

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/bulk"
        result = self.openbas.http_post(path, post_data=data, **kwargs)
        return result
