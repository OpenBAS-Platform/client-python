from typing import Any, cast

from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import GetWithoutIdMixin, UpdateMixin


class Me(RESTObject):
    _id_attr = None
    _repr_attr = "user_email"


class MeManager(GetWithoutIdMixin, UpdateMixin, RESTManager):
    _path = "/me"
    _obj_cls = Me

    def get(self, **kwargs: Any) -> Me:
        return cast(Me, super().get(**kwargs))
