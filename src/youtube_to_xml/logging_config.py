"""Logging configuration for YouTube transcript processing."""

import logging
from pathlib import Path


def setup_logging(log_file: str = "youtube_to_xml.log") -> None:
    """Set up logging configuration for the application.

    Args:
        log_file: Path to log file, defaults to 'youtube_to_xml.log'

    Configures logging with:
    - INFO level and above
    - File output with timestamps
    - Module name identification
    - Automatic log rotation handled by external tools if needed
    """
    log_path = Path(log_file)

    # Create logs directory if needed
    if log_path.parent != Path():
        log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filemode="a",  # Append to existing log file
    )

    # Also ensure console output for errors during development
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")
    console_handler.setFormatter(console_formatter)

    # Add console handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for the specified module.

    Args:
        name: Module name, typically __name__

    Returns:
        Logger instance configured for the module
    """
    return logging.getLogger(name)
