from pyobas.base import RESTManager, RESTObject
from pyobas.mixins import CreateMixin
from pyobas.utils import RequiredOptional


class InjectExpectationTrace(RESTObject):
    _id_attr = "inject_expectation_trace_id"

class InjectExpectationTraceManager(RESTManager,CreateMixin):
    _path = "/inject-expectations-traces"
    _obj_cls = InjectExpectationTrace
    _create_attrs = RequiredOptional(
        required=("inject_expectation_trace_expectation",
                  "inject_expectation_trace_collector",
                  "inject_expectation_trace_alert_name",
                  "inject_expectation_trace_alert_link",
                  "inject_expectation_trace_date",),
    )

