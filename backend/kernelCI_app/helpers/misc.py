from typing import Union, TypedDict, Optional
from kernelCI_app.helpers.filters import UNKNOWN_STRING
from kernelCI_app.utils import string_to_json


class Misc(TypedDict):
    platform: str


def handle_misc(misc: Union[str, dict, None]) -> Optional[Misc]:
    """Handle misc data (environment or build) by parsing JSON string or dict."""
    parsed_misc: Misc = {}

    if isinstance(misc, str):
        misc = string_to_json(misc)
        if misc is None:
            return None
    elif not isinstance(misc, dict):
        return None

    parsed_misc["platform"] = misc.get("platform", UNKNOWN_STRING)

    return parsed_misc


def misc_value_or_default(misc: Optional[Misc]) -> Misc:
    """Return misc data or default if None."""
    default_misc: Misc = {
        "platform": UNKNOWN_STRING,
    }

    if misc is not None:
        return misc
    return default_misc
