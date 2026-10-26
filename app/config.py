import os

from pathlib import Path

FIELDS = {
    "UT_SERVER_URL": {"type": str, "required": True},
    "UT_SERVER_NAME": {"type": str, "required": True},
    "UT_MOTD": {"type": list, "separator": "\n", "limit": 4, "multiline": True},
    "UT_ADMIN_NAME": {"type": str},
    "UT_ADMIN_EMAIL": {"type": str},
    "UT_ADMIN_PASSWORD": {"type": str, "strip": False},
    "UT_GAME_PASSWORD": {"type": str, "strip": False},
    "UT_WEB_USER": {"type": str},
    "UT_WEB_PASS": {"type": str, "strip": False},
    "UT_MAX_PLAYERS": {"type": int, "min": 1, "max": 128},
    "UT_UPLINK": {"type": bool},
    "UT_LAN_ENABLED": {"type": bool},
    "UT_WEB_ENABLED": {"type": bool, "default": False},
    "UT_SERVER_PACKAGES": {"type": list},
    "UT_MODS": {"type": list},
}


class ConfigError(Exception):
    pass


def _parse(name, spec, raw):
    kind = spec["type"]
    value = raw if spec.get("strip", True) is False else raw.strip()

    if not value:
        if spec.get("required"):
            raise ConfigError(f"{name} is required")

        return [] if kind is list else spec.get("default")

    for char in value:
        if char == "\n" and spec.get("multiline"):
            continue

        if ord(char) < 32 or ord(char) == 127 or char in "\u2028\u2029":
            raise ConfigError(f"{name} contains an invalid control character")

    if kind is bool:
        if value in ("True", "False"):
            return value == "True"

        raise ConfigError(f"{name} must be True or False")

    if kind is int:
        if not (value.isascii() and value.isdigit()):
            raise ConfigError(f"{name} must be an integer between {spec['min']} and {spec['max']}")

        number = int(value)

        if not spec["min"] <= number <= spec["max"]:
            raise ConfigError(f"{name} must be an integer between {spec['min']} and {spec['max']}")

        return number

    if kind is list:
        items = [item.strip() for item in value.split(spec.get("separator", ",")) if item.strip()]
        return items[: spec["limit"]] if "limit" in spec else items

    if kind is str:
        return value

    raise ConfigError(f"{name} has an unsupported type")


def _read(environ):
    return {name: _parse(name, spec, environ.get(name, "")) for name, spec in FIELDS.items()}


def load():
    home = Path(os.environ.get("UT_HOME", "/opt/ut99"))

    system_dir = home / "System"
    maps_dir = home / "Maps"

    state_dir = Path(os.environ.get("UT_STATE_DIR", "/var/lib/ut99"))
    config_dir = Path(os.environ.get("UT_CONFIG_DIR", "/config"))
    mods_dir = Path(os.environ.get("UT_MODS_DIR", "/mods"))

    config = _read(os.environ)

    if not (system_dir / "ucc-bin").is_file():
        raise ConfigError(f"ucc-bin not found: {system_dir / 'ucc-bin'}")

    if not maps_dir.is_dir():
        raise ConfigError(f"Maps directory not found: {maps_dir}")

    config.update(
        {
            "home": home,
            "system_dir": system_dir,
            "config_dir": config_dir,
            "state_dir": state_dir,
            "mods_dir": mods_dir,
            "template": config_dir / "UnrealTournament.ini.template",
            "state_template": state_dir / "UnrealTournament.ini.template",
            "ini": system_dir / "UnrealTournament.ini",
        }
    )

    return config


def ensure_template(config):
    if config["template"].is_file():
        return config["template"]

    fallback = config["state_template"]

    if fallback.is_file():
        return fallback

    source = config["ini"]

    if not source.is_file():
        raise ConfigError(f"Fresh install INI not found: {source}")

    try:
        fallback.parent.mkdir(parents=True, exist_ok=True)
        fallback.write_bytes(source.read_bytes())

    except OSError as exc:
        raise ConfigError(
            f"Unable to create template {fallback}: {exc}. "
            f"Ensure the state directory is writable by the container user."
        ) from exc

    return fallback
