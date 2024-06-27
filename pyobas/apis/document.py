from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject


class Document(RESTObject):
    _id_attr = "document_id"


class DocumentManager(RESTManager):
    _path = "/documents"
    _obj_cls = Document

    @exc.on_http_error(exc.OpenBASUpdateError)
    def download(self, document_id: str, **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/" + document_id + "/file"
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(
        self, document: Dict[str, Any], file: tuple, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/upsert"
        result = self.openbas.http_post(
            path, post_data=document, files={"file": file}, **kwargs
        )
        return result
