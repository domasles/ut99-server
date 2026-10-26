import tempfile
import os
import re

from pathlib import Path
from typing import Any


class IniError(Exception):
    pass


SECTION = re.compile(r"^\s*\[([^\]]+)\]\s*$")


# fmt: off
MAPPINGS = {
    "UT_SERVER_NAME": {
        "section": "Engine.GameReplicationInfo",
        "key": "ServerName",
    },
    "UT_MOTD": {
        "section": "Engine.GameReplicationInfo",
        "key": "MOTDLine",
        "kind": "series",
    },
    "UT_ADMIN_NAME": {
        "section": "Engine.GameReplicationInfo",
        "key": "AdminName",
    },
    "UT_ADMIN_EMAIL": {
        "section": "Engine.GameReplicationInfo",
        "key": "AdminEmail",
    },
    "UT_ADMIN_PASSWORD": {
        "section": "Engine.GameInfo",
        "key": "AdminPassword",
    },
    "UT_GAME_PASSWORD": {
        "section": "Engine.GameInfo",
        "key": "GamePassword",
    },
    "UT_WEB_USER": {
        "section": "UTServerAdmin.UTServerAdmin",
        "key": "AdminUsername"
    },
    "UT_WEB_PASSWORD": {
        "section": "UTServerAdmin.UTServerAdmin",
        "key": "AdminPassword",
    },
    "UT_MAX_PLAYERS": {
        "section": "Engine.GameInfo",
        "key": "MaxPlayers",
    },
    "UT_UPLINK": {
        "section": "Engine.GameEngine",
        "key": "ServerActors",
        "kind": "toggle",
        "prefix": "IpServer.UdpServerUplink",
        "values": [
            "IpServer.UdpServerUplink MasterServerAddress=master.333networks.com MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.qtracker.com MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.telefragged.com MasterServerPort=27500",
            "IpServer.UdpServerUplink MasterServerAddress=master.errorist.eu MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.hlkclan.net MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.openspy.net MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.oldunreal.com MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master2.oldunreal.com MasterServerPort=27900",
            "IpServer.UdpServerUplink MasterServerAddress=master.hypercoop.tk MasterServerPort=27900",
        ],
    },
    "UT_LAN_ENABLED": {
        "section": "IpDrv.UdpBeacon",
        "key": "DoBeacon",
    },
    "UT_WEB_ENABLED": {
        "section": "UWeb.WebServer",
        "key": "bEnabled",
    },
    "UT_SERVER_PACKAGES": {
        "section": "Engine.GameEngine",
        "key": "ServerPackages",
        "kind": "list",
    },
}
# fmt: on


def _bounds(lines: list[str]) -> dict[str, list[tuple[int, int]]]:
    headers = []

    for index, line in enumerate(lines):
        match = SECTION.match(line)

        if match:
            headers.append((index, match.group(1).strip()))

    result = {}

    for position, (index, name) in enumerate(headers):
        end = headers[position + 1][0] if position + 1 < len(headers) else len(lines)
        result.setdefault(name.lower(), []).append((index, end))

    return result


def _section(lines: list[str], name: str, create: bool = False) -> tuple[int, int]:
    matches = _bounds(lines).get(name.lower(), [])

    if not matches:
        if not create:
            raise IniError(f"Section [{name}] not found")

        lines.append(f"[{name}]")
        return len(lines) - 1, len(lines)

    if len(matches) > 1:
        raise IniError(f"Section [{name}] appears more than once")

    return matches[0]


def _key(line: str, key: str) -> re.Match[str] | None:
    return re.match(rf"\s*{re.escape(key)}\s*=", line, re.IGNORECASE)


def _value(line: str) -> str:
    return line.split("=", 1)[1].strip()


def set_key(lines: list[str], section: str, key: str, value: str) -> None:
    start, end = _section(lines, section, create=True)
    found = [i for i in range(start + 1, end) if _key(lines[i], key)]

    if len(found) > 1:
        raise IniError(f"Key {key} appears more than once in [{section}]")

    line = f"{key}={value}"

    if found:
        lines[found[0]] = line
        return

    insert_at = start + 1

    for i in range(start + 1, end):
        if lines[i].strip():
            insert_at = i + 1

    lines.insert(insert_at, line)


def add_list(lines: list[str], section: str, key: str, value: str) -> None:
    start, end = _section(lines, section, create=True)
    found = [i for i in range(start + 1, end) if _key(lines[i], key)]

    if any(_value(lines[i]).lower() == value.lower() for i in found):
        return

    lines.insert(found[-1] + 1 if found else start + 1, f"{key}={value}")


def remove_list(lines: list[str], section: str, key: str, prefix: str) -> None:
    matches = _bounds(lines).get(section.lower(), [])

    if not matches:
        return

    if len(matches) > 1:
        raise IniError(f"Section [{section}] appears more than once")

    start, end = matches[0]
    drop = [
        i
        for i in range(start + 1, end)
        if _key(lines[i], key) and _value(lines[i]).lower().startswith(prefix.lower())
    ]

    for i in reversed(drop):
        del lines[i]


def _clear_section_keys(lines: list[str], section: str, key: str) -> None:
    matches = _bounds(lines).get(section.lower(), [])

    if not matches:
        return

    if len(matches) > 1:
        raise IniError(f"Section [{section}] appears more than once")

    start, end = matches[0]
    drop = [i for i in range(start + 1, end) if _key(lines[i], key)]

    for i in reversed(drop):
        del lines[i]


def _clear_section_series(lines: list[str], section: str, base: str) -> None:
    matches = _bounds(lines).get(section.lower(), [])

    if not matches:
        return

    if len(matches) > 1:
        raise IniError(f"Section [{section}] appears more than once")

    start, end = matches[0]

    drop = [
        i
        for i in range(start + 1, end)
        if lines[i].split("=", 1)[0].strip().startswith(base)
    ]

    for i in reversed(drop):
        del lines[i]


def render(template: str, config: dict[str, Any]) -> list[str]:
    lines = template.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    for env_name, spec in MAPPINGS.items():
        value = config.get(env_name)
        kind = spec.get("kind", "set")
        section = spec["section"]
        key = spec["key"]

        if kind == "set":
            set_key(lines, section, key, "" if value is None else str(value))

        elif kind == "list":
            if value:
                for item in value:
                    add_list(lines, section, key, item)

            else:
                _clear_section_keys(lines, section, key)

        elif kind == "series":
            if value:
                for index, item in enumerate(value, 1):
                    set_key(lines, section, f"{key}{index}", item)

            else:
                _clear_section_series(lines, section, key)

        elif kind == "toggle":
            if value is True:
                remove_list(lines, section, key, spec["prefix"])

                values = spec["values"] if "values" in spec else [spec["value"]]

                for v in values:
                    add_list(lines, section, key, v)

            else:
                remove_list(lines, section, key, spec["prefix"])

    return lines


def write(path: Path, lines: list[str]) -> None:
    text = "\n".join(lines)

    if text and not text.endswith("\n"):
        text += "\n"

    path.parent.mkdir(parents=True, exist_ok=True)

    if (path.is_file() and path.read_text(encoding="utf-8", errors="surrogateescape") == text):  # fmt: skip
        return

    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")  # fmt: skip

    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", errors="surrogateescape", newline="") as handle:  # fmt: skip
            handle.write(text)

        os.chmod(temporary, 0o600)
        os.replace(temporary, path)

    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
