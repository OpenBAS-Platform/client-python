from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import CreateMixin, GetMixin, ListMixin, UpdateMixin
from pyobas.utils import RequiredOptional


class Injector(RESTObject):
    pass


class InjectorManager(GetMixin, ListMixin, CreateMixin, UpdateMixin, RESTManager):
    _path = "/injectors"
    _obj_cls = Injector
    _create_attrs = RequiredOptional(
        required=("injector_id", "injector_name", "injector_type", "injector_contracts")
    )
