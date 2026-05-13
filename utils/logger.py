import logging
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOG_DIR = PROJECT_ROOT / "logs"
DEFAULT_LOG_FILE = "automation.log"
DEFAULT_BACKUP_COUNT = 14
LOGGER_NAME = "ness_automation"


def _log_level_from_env() -> int:
    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    return getattr(logging, level_name, logging.INFO)


def _log_dir_from_env() -> Path:
    return Path(os.environ.get("LOG_DIR", str(DEFAULT_LOG_DIR))).expanduser()


def _backup_count_from_env() -> int:
    raw_value = os.environ.get("LOG_BACKUP_COUNT", str(DEFAULT_BACKUP_COUNT))
    try:
        return max(0, int(raw_value))
    except ValueError:
        return DEFAULT_BACKUP_COUNT


def build_daily_file_handler(
    log_file: Path,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> TimedRotatingFileHandler:
    """Create a file handler that rotates every 24 hours."""

    log_file.parent.mkdir(parents=True, exist_ok=True)
    handler = TimedRotatingFileHandler(
        filename=log_file,
        when="D",
        interval=1,
        backupCount=backup_count,
        encoding="utf-8",
        delay=True,
    )
    handler.set_name("daily_file")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(processName)s | %(message)s"
        )
    )
    return handler


def configure_logging(
    logger_name: str = LOGGER_NAME,
    log_dir: Path | None = None,
    log_file_name: str = DEFAULT_LOG_FILE,
    backup_count: int | None = None,
) -> logging.Logger:
    """Configure the project logger with 24-hour backup rotation."""

    logger = logging.getLogger(logger_name)
    logger.setLevel(_log_level_from_env())
    logger.propagate = False

    if any(handler.get_name() == "daily_file" for handler in logger.handlers):
        return logger

    resolved_log_dir = log_dir or _log_dir_from_env()
    resolved_backup_count = (
        _backup_count_from_env() if backup_count is None else backup_count
    )
    handler = build_daily_file_handler(
        resolved_log_dir / log_file_name,
        backup_count=resolved_backup_count,
    )
    handler.setLevel(_log_level_from_env())
    logger.addHandler(handler)
    return logger


def get_logger(name: str | None = None) -> logging.Logger:
    """Return a child logger from the configured automation logger."""

    configure_logging()
    if not name:
        return logging.getLogger(LOGGER_NAME)
    return logging.getLogger(f"{LOGGER_NAME}.{name}")
