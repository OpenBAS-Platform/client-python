from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Tag(RESTObject):
    _id_attr = "tag_id"


class TagManager(RESTManager):
    _path = "/tags"
    _obj_cls = Tag

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(self, data: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/upsert"
        result = self.openbas.http_post(path, post_data=data, **kwargs)
        return result
