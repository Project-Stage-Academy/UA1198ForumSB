from projects.models import Project
from django.core.exceptions import ValidationError


def check_instance(instance):
    if not isinstance(instance, Project):
        raise ValidationError("Object must be an instance of Project")

def get_changed_fields(old_instance, new_instance):
    """
    Function compare project data and return changed
    """
    check_instance(old_instance)
    check_instance(new_instance)

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
