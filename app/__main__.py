import subprocess
import signal
import time
import sys
import os

from app.config import ConfigError, ensure_template, load
from app.ini import IniError, render, write


class LaunchError(Exception):
    pass


def launch(config):
    try:
        os.chdir(config["system_dir"])

    except OSError as exc:
        raise LaunchError(str(exc)) from exc

    redeemod_cli = os.environ.get("REDEEMOD_CLI", "/opt/ut99/redeemod/redeemod-cli")
    command = [redeemod_cli, "launch", "ut99"]

    mods = config.get("UT_MODS") or []

    if mods:
        command.extend(str(config["mods_dir"] / mod) for mod in mods)

    command.extend(["--flags", f"server {config['UT_SERVER_URL']}"])
    process = subprocess.Popen(command, cwd=".", start_new_session=True)

    def _shutdown(signum, frame):
        try:
            os.killpg(process.pid, signal.SIGTERM)

        except OSError:
            pass

        raise SystemExit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    while True:
        try:
            os.killpg(process.pid, 0)

        except ProcessLookupError:
            break

        time.sleep(1)


def main():
    try:
        config = load()
        template_path = ensure_template(config)

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
