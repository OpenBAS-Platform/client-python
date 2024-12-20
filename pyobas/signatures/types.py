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
    SIG_TYPE_IPV4 = "ipv4_address"
    SIG_TYPE_IPV6 = "ipv6_address"
