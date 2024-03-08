from typing import Any, cast

from pybas.base import RESTManager, RESTObject
from pybas.mixins import GetWithoutIdMixin
from pybas.types import RequiredOptional


class Me(RESTObject):
    _id_attr = None
    _repr_attr = "user_email"


class MeManager(GetWithoutIdMixin, RESTManager):
    _path = "/me"
    _obj_cls = Me
    _update_attrs = RequiredOptional(
        optional=("user_email", "user_firstname", "user_lastname")
    )

    def get(self, **kwargs: Any) -> Me:
        return cast(Me, super().get(**kwargs))
