import sys
import os

from pathlib import Path

from app.config import ConfigError, ensure_template, load
from app.ini import IniError, render, write


class LaunchError(Exception):
    pass


def apply_mods():
    # TODO: run RedeeMOD CLI for potential mods
    pass


def launch(config):
    try:
        os.chdir(config["system_dir"])

    except OSError as exc:
        raise LaunchError(str(exc)) from exc

    command = ["./ucc-bin", "server", config["UT_SERVER_URL"]]
    os.execvp(command[0], command)


def main():
    try:
        config = load()
        template_path = ensure_template(config)

        apply_mods()

        template = template_path.read_text(encoding="utf-8", errors="surrogateescape")

        write(config["ini"], render(template, config))
        launch(config)

    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    except IniError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    except (LaunchError, OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 4

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
