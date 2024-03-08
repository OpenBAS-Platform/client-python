from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import ListMixin, UpdateMixin


class Organization(RESTObject):
    pass


class OrganizationManager(ListMixin, UpdateMixin, RESTManager):
    _path = "/organizations"
    _obj_cls = Organization
