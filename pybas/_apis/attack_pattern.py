from typing import Any, Dict, List

from pybas import exceptions as exc
from pybas.base import RESTManager, RESTObject


class AttackPatternPhase(RESTObject):
    _id_attr = "attack_pattern_id"


class AttackPatternManager(RESTManager):
    _path = "/attack_patterns"
    _obj_cls = AttackPatternPhase

    @exc.on_http_error(exc.OpenBASUpdateError)
    def upsert(
        self, attack_patterns: List[Dict[str, Any]], **kwargs: Any
    ) -> Dict[str, Any]:
        data = {"attack_patterns": attack_patterns}
        path = f"{self.path}/upsert"
        result = self.openbas.http_post(path, post_data=data, **kwargs)
        return result
