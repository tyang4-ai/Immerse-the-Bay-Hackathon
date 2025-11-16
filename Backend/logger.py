"""
Structured logging module for HoloHuman XR Backend

Provides:
- Request ID tracking
- Performance timing
- Error ID generation
- Structured log formatting
"""

import logging
import uuid
import time
from functools import wraps
from datetime import datetime
from typing import Optional

# Configure logging format (request_id added via filter, not format string)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

class RequestIDFilter(logging.Filter):
    """Add request_id to log records if not present"""
    def filter(self, record):
        if not hasattr(record, 'request_id'):
            record.request_id = 'SYSTEM'
        return True

# Add filter to root logger
for handler in logging.root.handlers:
    handler.addFilter(RequestIDFilter())

class RequestLogger:
    """Logger with request ID context"""

    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.request_id = None

    def set_request_id(self, request_id: Optional[str] = None):
        """Set or generate request ID for current context"""
        self.request_id = request_id or self.generate_request_id()
        return self.request_id

    @staticmethod
    def generate_request_id() -> str:
        """Generate unique request ID"""
        return f"REQ-{uuid.uuid4().hex[:8].upper()}"

    @staticmethod
    def generate_error_id() -> str:
        """Generate unique error ID"""
        return f"ERR-XR-{uuid.uuid4().hex[:6].upper()}"

    def _log(self, level, message, **kwargs):
        """Internal log method with request ID"""
        extra = {'request_id': self.request_id or 'INIT'}
        extra.update(kwargs)
        self.logger.log(level, message, extra=extra)

    def debug(self, message, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)

    def info(self, message, **kwargs):
        self._log(logging.INFO, message, **kwargs)

    def warning(self, message, **kwargs):
        self._log(logging.WARNING, message, **kwargs)

    def error(self, message, **kwargs):
        self._log(logging.ERROR, message, **kwargs)

    def critical(self, message, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)


def timer(func):
    """Decorator to log function execution time"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed_ms = (time.time() - start_time) * 1000
            logger = logging.getLogger(func.__module__)
            logger.info(
                f"{func.__name__} completed in {elapsed_ms:.2f}ms",
                extra={'request_id': 'TIMER'}
            )
            return result
        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger = logging.getLogger(func.__module__)
            logger.error(
                f"{func.__name__} failed after {elapsed_ms:.2f}ms: {str(e)}",
                extra={'request_id': 'TIMER'}
            )
            raise
    return wrapper


class PerformanceTimer:
    """Context manager for performance timing"""

    def __init__(self, operation_name: str, logger: RequestLogger):
        self.operation_name = operation_name
        self.logger = logger
        self.start_time = None
        self.elapsed_ms = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Started: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed_ms = (time.time() - self.start_time) * 1000
        if exc_type is None:
            self.logger.info(f"Completed: {self.operation_name} ({self.elapsed_ms:.2f}ms)")
        else:
            self.logger.error(f"Failed: {self.operation_name} ({self.elapsed_ms:.2f}ms) - {exc_val}")
        return False  # Don't suppress exceptions


# Module-level loggers for each backend component
api_logger = RequestLogger('ecg_api')
model_logger = RequestLogger('model_loader')
hr_logger = RequestLogger('heartrate_analyzer')
mapper_logger = RequestLogger('region_mapper')
llm_logger = RequestLogger('clinical_llm')


# Example usage:
if __name__ == '__main__':
    # Test logging
    api_logger.set_request_id()
    api_logger.info("Backend initialized")
    api_logger.debug("Debug message with details", extra={'key': 'value'})

    # Test error ID generation
    error_id = RequestLogger.generate_error_id()
    api_logger.error(f"Test error with ID: {error_id}")

    # Test performance timer
    with PerformanceTimer("test_operation", api_logger):
        time.sleep(0.1)

    print(f"Generated request ID: {api_logger.request_id}")
    print(f"Generated error ID: {error_id}")