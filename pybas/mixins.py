from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple, Type, Union

import requests

import pybas
from pybas import base
from pybas import exceptions as exc
from pybas import utils

__all__ = [
    "GetMixin",
    "GetWithoutIdMixin",
]

if TYPE_CHECKING:
    # When running mypy we use these as the base classes
    _RestManagerBase = base.RESTManager
    _RestObjectBase = base.RESTObject
else:
    _RestManagerBase = object
    _RestObjectBase = object


class HeadMixin(_RestManagerBase):
    @exc.on_http_error(exc.OpenBASHeadError)
    def head(
        self, id: Optional[Union[str, int]] = None, **kwargs: Any
    ) -> "requests.structures.CaseInsensitiveDict[Any]":
        if TYPE_CHECKING:
            assert self.path is not None

        path = self.path
        if id is not None:
            path = f"{path}/{utils.EncodedId(id)}"

        return self.openbas.http_head(path, **kwargs)


class GetMixin(HeadMixin, _RestManagerBase):
    _computed_path: Optional[str]
    _from_parent_attrs: Dict[str, Any]
    _obj_cls: Optional[Type[base.RESTObject]]
    _optional_get_attrs: Tuple[str, ...] = ()
    _parent: Optional[base.RESTObject]
    _parent_attrs: Dict[str, Any]
    _path: Optional[str]
    openbas: pybas.OpenBAS

    @exc.on_http_error(exc.OpenBASGetError)
    def get(
        self, id: Union[str, int], lazy: bool = False, **kwargs: Any
    ) -> base.RESTObject:
        if isinstance(id, str):
            id = utils.EncodedId(id)
        path = f"{self.path}/{id}"
        if TYPE_CHECKING:
            assert self._obj_cls is not None
        if lazy is True:
            if TYPE_CHECKING:
                assert self._obj_cls._id_attr is not None
            return self._obj_cls(self, {self._obj_cls._id_attr: id}, lazy=lazy)
        server_data = self.openbas.http_get(path, **kwargs)
        if TYPE_CHECKING:
            assert not isinstance(server_data, requests.Response)
        return self._obj_cls(self, server_data, lazy=lazy)


class GetWithoutIdMixin(HeadMixin, _RestManagerBase):
    _computed_path: Optional[str]
    _from_parent_attrs: Dict[str, Any]
    _obj_cls: Optional[Type[base.RESTObject]]
    _optional_get_attrs: Tuple[str, ...] = ()
    _parent: Optional[base.RESTObject]
    _parent_attrs: Dict[str, Any]
    _path: Optional[str]
    openbas: pybas.OpenBAS

    @exc.on_http_error(exc.OpenBASGetError)
    def get(self, **kwargs: Any) -> base.RESTObject:
        if TYPE_CHECKING:
            assert self.path is not None
        server_data = self.openbas.http_get(self.path, **kwargs)
        if TYPE_CHECKING:
            assert not isinstance(server_data, requests.Response)
            assert self._obj_cls is not None
        return self._obj_cls(self, server_data)
