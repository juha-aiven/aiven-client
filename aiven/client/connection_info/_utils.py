# Copyright (c) 2021 Aiven, Helsinki, Finland. https://aiven.io/
from .common import ConnectionInfoError
from aiven.client.common import UNDEFINED
from typing import Any, Mapping, Optional, Sequence, TypeVar, Union

import ipaddress
import urllib.parse

T = TypeVar("T")


def find_component(items: Sequence[Mapping[str, T]], **filters: Union[object, str]) -> Mapping[str, T]:
    for item in items:
        if all(key in item and item[key] == value for key, value in filters.items() if value is not UNDEFINED):
            return item
    msg_filters = ", ".join(f"{field}={value}" for field, value in filters.items())
    raise ConnectionInfoError(f"Could not find connection information with filters {msg_filters}")


def find_user(service: Mapping[str, Any], username: str) -> Mapping[str, Any]:
    for user in service["users"]:
        if user["username"] == username:
            return user
    raise ConnectionInfoError(f"Could not find connection information for username {username}")


def format_uri(
    *,
    scheme: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    netloc: Optional[str] = None,
    path: str = "",
    query: Optional[Mapping[str, Any]] = None,
    fragment: str = "",
) -> str:
    if netloc is None:
        bits = []
        if username is not None:
            bits.append(urllib.parse.quote(username))
        if password is not None:
            bits.append(":")
            bits.append(urllib.parse.quote(password))
        if username is not None or password is not None:
            bits.append("@")
        if host is not None:
            try:
                ip = ipaddress.ip_address(host)
            except ValueError:
                # host not parseable as an IP address -> probably DNS name
                pass
            else:
                if ip.version == 4:
                    host = f"{ip}"
                elif ip.version == 6:
                    host = f"[{ip}]"
                else:
                    raise NotImplementedError(ip.version)
            bits.append(host)
            if port is not None and port != {"http": 80, "https": 443}.get(scheme.lower()):
                bits.append(f":{port}")
        netloc = "".join(bits)
    encoded_query = urllib.parse.urlencode(query) if query is not None else None
    return urllib.parse.urlunsplit((scheme, netloc, path, encoded_query, fragment))
