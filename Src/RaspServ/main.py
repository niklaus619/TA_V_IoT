"""Gemeinsamer Startpunkt fuer Datenbank, Modbus TCP und Weboberflaeche."""

import logging

from app import run


def main():
    try:
        run()
    except PermissionError as exc:
        logging.error(
            "Start fehlgeschlagen: %s. Fuer Modbus-Port 502 wird eine "
            "Bindeberechtigung benoetigt (siehe raspserv.service). "
            "Der Datenbankordner muss ebenfalls beschreibbar sein.",
            exc,
        )
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
