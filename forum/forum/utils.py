from typing import Any

from django.template.loader import render_to_string


def build_email_message(
    email_template_path: str,
    context: dict[str, Any] | None = None
) -> str:
    return render_to_string(
        email_template_path,
        context
    )
