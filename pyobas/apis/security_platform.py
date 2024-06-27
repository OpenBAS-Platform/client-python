from typing import Any, Dict

from pyobas import exceptions as exc
from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import CreateMixin, GetMixin, ListMixin, UpdateMixin
from pyobas.utils import RequiredOptional


class SecurityPlatform(RESTObject):
    pass


class SecurityPlatformManager(
    GetMixin, ListMixin, CreateMixin, UpdateMixin, RESTManager
):
    _path = "/security_platforms"
    _obj_cls = SecurityPlatform
    _create_attrs = RequiredOptional(
        required=("asset_name", "security_platform_type"),
        optional=(
            "asset_description",
            "security_platform_logo_light",
            "security_platform_logo_dark",
        ),
    )

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(
        self, security_platform: Dict[str, Any], **kwargs: Any
    ) -> Dict[str, Any]:
        path = f"{self.path}/upsert"
        result = self.openbas.http_post(path, post_data=security_platform, **kwargs)
        return result
