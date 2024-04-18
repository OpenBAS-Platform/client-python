from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import CreateMixin, GetMixin, ListMixin, UpdateMixin
from pyobas.utils import RequiredOptional


class Collector(RESTObject):
    pass


class CollectorManager(GetMixin, ListMixin, CreateMixin, UpdateMixin, RESTManager):
    _path = "/collectors"
    _obj_cls = Collector
    _create_attrs = RequiredOptional(
        required=(
            "collector_id",
            "collector_name",
            "collector_type",
            "collector_period",
        )
    )
