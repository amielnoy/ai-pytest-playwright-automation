import logging
from logging.handlers import TimedRotatingFileHandler

from utils.logger import (
    DEFAULT_BACKUP_COUNT,
    build_daily_file_handler,
    configure_logging,
    get_logger,
    log_annotated_call,
)


def test_build_daily_file_handler_rotates_every_24_hours(tmp_path):
    handler = build_daily_file_handler(tmp_path / "automation.log")

    assert isinstance(handler, TimedRotatingFileHandler)
    assert handler.when == "D"
    assert handler.interval == 24 * 60 * 60
    assert handler.backupCount == DEFAULT_BACKUP_COUNT

    handler.close()


def test_configure_logging_adds_one_daily_file_handler(tmp_path):
    logger_name = "test_logger_config"
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()

    first = configure_logging(logger_name=logger_name, log_dir=tmp_path, backup_count=3)
    second = configure_logging(logger_name=logger_name, log_dir=tmp_path, backup_count=3)

    daily_handlers = [
        handler for handler in second.handlers if handler.get_name() == "daily_file"
    ]
    assert first is second
    assert len(daily_handlers) == 1
    assert isinstance(daily_handlers[0], TimedRotatingFileHandler)
    assert daily_handlers[0].backupCount == 3

    for handler in second.handlers:
        handler.close()
    second.handlers.clear()


def test_get_logger_returns_child_logger():
    logger = get_logger("unit")

    assert logger.name == "ai_automation.unit"


def test_log_annotated_call_logs_primitive_annotated_arguments(caplog):
    logger = logging.getLogger("test_annotated_call")
    logger.setLevel(logging.INFO)

    @log_annotated_call(logger)
    def sample(query: str, max_price: float, helper: object) -> str:
        return query

    with caplog.at_level(logging.INFO, logger="test_annotated_call"):
        result = sample("MacBook", 2000.0, object())

    assert result == "MacBook"
    assert ".sample(query='MacBook', max_price=2000.0)" in caplog.text
    assert "helper=" not in caplog.text


def test_log_annotated_call_uses_function_metadata():
    @log_annotated_call(logging.getLogger("test_metadata"))
    def sample(query: str) -> str:
        return query

    assert sample.__name__ == "sample"
