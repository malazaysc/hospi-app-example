#!/usr/bin/env python3
"""
Generate sample property data against the project's Postgres/PostGIS database.

This is a thin wrapper around the `seed_data` Django management command so the
seeding logic stays in one place. Prefer running `python manage.py seed_data`
directly; this script exists for convenience.
"""

import argparse
import os
import sys
from pathlib import Path

import django
from django.core.management import call_command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--clear", action="store_true")
    args = parser.parse_args()

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hospi.settings")
    django.setup()

    call_command("seed_data", count=args.count, clear=args.clear)


if __name__ == "__main__":
    main()
