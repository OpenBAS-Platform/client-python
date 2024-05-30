from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import ListMixin, UpdateMixin
from pyobas.utils import RequiredOptional


class InjectExpectation(RESTObject):
    _id_attr = "inject_expectation_id"


class InjectExpectationManager(ListMixin, UpdateMixin, RESTManager):
    _path = "/injects/expectations"
    _obj_cls = InjectExpectation
    _update_attrs = RequiredOptional(required=("collector_id", "result", "is_success"))

    @exc.on_http_error(exc.OpenBASUpdateError)
    def expectations_for_source(self, source_id: str, **kwargs: Any) -> Dict[str, Any]:
        path = f"{self.path}/" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def expectations_assets_for_source(
        self, source_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/assets/" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def prevention_expectations_for_source(
        self, source_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/prevention" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def detection_expectations_for_source(
        self, source_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/detection/" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def update(
        self,
        inject_expectation_id: str,
        inject_expectation: Dict[str, Any],
        **kwargs: Any,
    ) -> Dict[str, Any]:
        path = f"{self.path}/{inject_expectation_id}"
        result = self.openbas.http_put(path, post_data=inject_expectation, **kwargs)
        return result
