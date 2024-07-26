import logging
from typing import Dict, Literal, Optional


class ColoredFormatter(logging.Formatter):
    grey = "\x1b[38;20m"
    green = "\u001b[32m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    magenta = "\u001b[35m"
    reset = "\x1b[0m"

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: Literal['%', '{', '$'] = '%',
        validate: bool = True,
        *,
        defaults: Optional[Dict] = None
    ) -> None:
        super().__init__(fmt, datefmt, style, validate, defaults=defaults)
        self.FORMATS = {
            logging.DEBUG: logging.Formatter(self.grey + self._fmt + self.reset),
            logging.INFO: logging.Formatter(self.green + self._fmt + self.reset),
            logging.WARNING: logging.Formatter(self.yellow + self._fmt + self.reset),
            logging.ERROR: logging.Formatter(self.red + self._fmt + self.reset),
            logging.CRITICAL: logging.Formatter(self.magenta + self._fmt + self.reset)
        }

    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno)

        if not log_fmt:
            return self.FORMATS.get(logging.INFO)

        return log_fmt.format(record)


logger = logging.getLogger("django")
