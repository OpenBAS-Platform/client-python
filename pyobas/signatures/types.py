from enum import Enum


class MatchTypes(str, Enum):
    MATCH_TYPE_FUZZY = "fuzzy"
    MATCH_TYPE_SIMPLE = "simple"


class SignatureTypes(str, Enum):
    SIG_TYPE_PARENT_PROCESS_NAME = "parent_process_name"
    SIG_TYPE_HOSTNAME = "hostname"
    SIG_TYPE_PROCESS_NAME = "process_name"
    SIG_TYPE_COMMAND_LINE = "command_line"
    SIG_TYPE_FILE_NAME = "file_name"
    SIG_TYPE_SOURCE_IPV4 = "source_ipv4_address"
    SIG_TYPE_TARGET_IPV4 = "target_ipv4_address"
    SIG_TYPE_SOURCE_IPV6 = "source_ipv6_address"
    SIG_TYPE_TARGET_IPV6 = "target_ipv6_address"
