from html import escape

from forum.logging import logger


def escape_xss(value):
    escaped_value = escape(value, quote=False)
    if value != escaped_value:
        logger.warning("Input contains potential XSS content.")
    return escaped_value