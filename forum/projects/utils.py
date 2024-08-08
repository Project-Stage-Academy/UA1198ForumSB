from projects.models import Project
from django.core.exceptions import ValidationError


def get_changed_fields(old_instance, new_instance):
    """
    Function compare project data and return changed
    """

    if not (isinstance(old_instance, Project) and isinstance(old_instance, Project)):
        raise ValidationError("Object must be an instance of Project")

    changes = {}
    for field in old_instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(new_instance, field_name)
        if old_value != new_value:
            changes[field_name] = {
                'old': old_value,
                'new': new_value
            }
    return changes
