from enum import Enum


class MatchTypes(Enum):
    MATCH_TYPE_FUZZY = "fuzzy"
    MATCH_TYPE_SIMPLE = "simple"


class SignatureTypes(Enum):
    SIG_TYPE_PARENT_PROCESS_NAME = "parent_process_name"
    SIG_TYPE_HOSTNAME = "hostname"
