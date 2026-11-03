"""Placeholder entry point: ``uv run python -m brave.worker``."""

import logging

logging.basicConfig(level=logging.INFO)


def main() -> None:
    logging.getLogger("brave.worker").info(
        "Worker placeholder - no queue configured yet (Dramatiq vs Celery to be decided)."
    )


if __name__ == "__main__":
    main()
