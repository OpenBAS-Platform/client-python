from enum import Enum


class MatchTypes(str, Enum):
    MATCH_TYPE_FUZZY = "fuzzy"
    MATCH_TYPE_SIMPLE = "simple"


class SignatureTypes(str, Enum):
    SIG_TYPE_PARENT_PROCESS_NAME = "parent_process_name"
    SIG_TYPE_SOURCE_IPV4_ADDRESS = "source_ipv4_address"
    SIG_TYPE_SOURCE_IPV6_ADDRESS = "source_ipv6_address"
    SIG_TYPE_TARGET_IPV4_ADDRESS = "target_ipv4_address"
    SIG_TYPE_TARGET_IPV6_ADDRESS = "target_ipv6_address"
    SIG_TYPE_TARGET_HOSTNAME_ADDRESS = "target_hostname_address"
    SIG_TYPE_START_DATE = "start_date"
    SIG_TYPE_END_DATE = "end_date"
