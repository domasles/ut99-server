#!/usr/bin/env bash
set -euo pipefail

UT_USER="${UT_USER:-server}"

UT_HOME="${UT_HOME:-/opt/ut99}"
UT_STATE_DIR="${UT_STATE_DIR:-/var/lib/ut99}"

UT_CONFIG_DIR="${UT_CONFIG_DIR:-/config}"
UT_MODS_DIR="${UT_MODS_DIR:-/mods}"

REDEEMOD_CLI="${REDEEMOD_CLI:-/opt/ut99/redeemod/redeemod-cli}"

cd "$UT_HOME"

if [ "$(id -u)" -eq 0 ]; then
    chown -R "$UT_USER:$UT_USER" "$UT_STATE_DIR"
    exec setpriv --reuid="$(id -u "$UT_USER")" --regid="$(id -g "$UT_USER")" --init-groups python3 -m app
fi

exec python3 -m app
