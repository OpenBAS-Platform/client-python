from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.apis.inject_expectation.model import (
    DetectionExpectation,
    ExpectationTypeEnum,
    PreventionExpectation,
)
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
    def expectations_assets_for_source(
        self, source_id: str, expiration_time: int = None, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/assets/" + source_id
        result = self.openbas.http_get(
            path,
            query_data=(
                {"expiration_time": expiration_time} if expiration_time else None
            ),
            **kwargs,
        )
        return result

    def expectations_models_for_source(self, source_id: str, **kwargs: Any):
        """Returns all expectations from OpenBAS that have had no result yet
            from the source_id (e.g. collector).

        :param source_id: the identifier of the collector requesting expectations
        :type source_id: str
        :param kwargs: additional data to pass to the endpoint
        :type kwargs: dict, optional

        :return: a list of expectation objects
        :rtype: list[DetectionExpectation|PreventionExpectation]
        """
        # TODO: we should implement a more clever mechanism to obtain
        #   specialised Expectation instances rather than just if/elseing
        #   through this list of possibilities.
        expectations = []
        for expectation_dict in self.expectations_assets_for_source(
            source_id=source_id, **kwargs
        ):
            if (
                expectation_dict["inject_expectation_type"]
                == ExpectationTypeEnum.Detection.value
            ):
                expectations.append(
                    DetectionExpectation(**expectation_dict, api_client=self)
                )
            elif (
                expectation_dict["inject_expectation_type"]
                == ExpectationTypeEnum.Prevention.value
            ):
                expectations.append(
                    PreventionExpectation(**expectation_dict, api_client=self)
                )
            else:
                expectations.append(
                    PreventionExpectation(**expectation_dict, api_client=self)
                )
        return expectations

    @exc.on_http_error(exc.OpenBASUpdateError)
    def prevention_expectations_for_source(
        self, source_id: str, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/prevention" + source_id
        result = self.openbas.http_get(path, **kwargs)
        return result

    @exc.on_http_error(exc.OpenBASUpdateError)
    def detection_expectations_for_source(
        self, source_id: str, expiration_time: int = None, **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/detection/" + source_id
        result = self.openbas.http_get(
            path,
            query_data=(
                {"expiration_time": expiration_time} if expiration_time else None
            ),
            **kwargs,
        )
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

    @exc.on_http_error(exc.OpenBASUpdateError)
    def bulk_update(
        self,
        inject_expectation_input_by_id: Dict[str, Dict[str, Any]],
        **kwargs: Any,
    ) -> None:
        path = f"{self.path}/bulk"
        self.openbas.http_put(
            path, post_data={"inputs": inject_expectation_input_by_id}, **kwargs
        )
