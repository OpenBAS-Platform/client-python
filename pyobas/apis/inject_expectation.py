from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import ListMixin, UpdateMixin


class InjectExpectation(RESTObject):
    pass


class InjectExpectationManager(ListMixin, UpdateMixin, RESTManager):
    _path = "/injects/expectations"
    _obj_cls = InjectExpectation

    @exc.on_http_error(exc.OpenBASUpdateError)
    def expectations_for_source(self, source_id: str, **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result
