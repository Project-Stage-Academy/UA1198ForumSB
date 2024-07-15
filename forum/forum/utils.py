from typing import Any

from django.template.loader import render_to_string


def build_email_message(
    email_template_path: str,
    context: dict[str, Any] = None
) -> str:
    return render_to_string(
        email_template_path,
        context
    )

def get_changed_fields(old_instance, new_instance):
    """
    Comparing model fields for any changes from old and new (updated) 
    Project instance
    """
    changed_fields = {}
    for field in old_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)
        if old_value != new_value:
            changed_fields[field_name] = {
                'old': old_value,
                'new': new_value
            }
    return changed_fields